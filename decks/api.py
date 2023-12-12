import logging

from django.db.models import Sum, F
from ninja import Router

from constants import PlayerCounts
from decks.constants import FIRST_ARKHAMDB_DECKLIST_DATE
from decks.models import DeckList, DeckCard, CardInfo
from decks.schemas import (
    DeckListBreakdownSchema,
    DecklistsRequestSchema,
)
from fuzzywuzzy import fuzz

router = Router()

from datetime import date, timedelta, datetime

from decks.arkhamdb import (
    retrieve_arkhamdb_decklists_by_date,
    retrieve_arkhamdb_decklist_metadata,
    ArkhamDBDecklistResponse,
    retrieve_arkhamdb_decklist_by_id,
)

# Download NLTK resources
import nltk

nltk.download("punkt")
nltk.download("stopwords")


def determine_player_count(
    deck_title: str, deck_description: str | None, tags: list[str]
) -> PlayerCounts:
    keyword_dict = {
        1: [
            "solo",
            "single",
            "single-player",
            "alone",
            "one player",
            "1 player",
            "1-player",
            "one-player",
            "single player",
        ],
        2: [
            "two-handed",
            "two handed",
            "2 handed",
            "2-handed",
            "duo",
            "pair",
            "2 players",
            "two players",
            "2-player",
            "two-player",
            "partner",
        ],
        4: [
            "four players",
            "4 players",
            "4 player",
            "four player",
            "4-player",
            "four-player",
            "group",
            "team",
            "quad",
        ],
    }
    # Check the tags first
    if "solo" in [tag.lower() for tag in tags]:
        return PlayerCounts.SOLO
    elif "multiplayer" in [tag.lower() for tag in tags]:
        keyword_dict = {  # Restrict to multiplayer options
            2: keyword_dict[2],
            4: keyword_dict[4],
        }

    highest_score = 0
    num_players = PlayerCounts.UNKNOWN

    # Check the deck title
    for players, keywords in keyword_dict.items():
        for keyword in keywords:
            score = fuzz.partial_ratio(keyword, deck_title.lower())
            if score > highest_score:
                highest_score = score
                num_players = players

    # If the highest score in the title is convincing enough, return it
    if highest_score > 60:
        if num_players == 1:
            return PlayerCounts.SOLO
        elif num_players == 2:
            return PlayerCounts.TWO_PLAYER
        elif num_players == 4:
            return PlayerCounts.FOUR_PLAYER

    # Check the deck description
    for players, keywords in keyword_dict.items():
        for keyword in keywords:
            score = fuzz.partial_ratio(keyword, deck_description.lower())
            if score > highest_score:
                highest_score = score
                num_players = players

    if highest_score > 60:
        if num_players == 1:
            return PlayerCounts.SOLO
        elif num_players == 2:
            return PlayerCounts.TWO_PLAYER
        elif num_players == 4:
            return PlayerCounts.FOUR_PLAYER
    else:
        return PlayerCounts.UNKNOWN


def determine_deck_campaign_standalone():
    pass


def save_decklist_info(decklist: ArkhamDBDecklistResponse):
    deck_info = decklist.dict(by_alias=False)
    logging.error(deck_info)
    deck_id = deck_info.pop("deck_id")
    deck, _ = DeckList.objects.get_or_create(deck_id=deck_id, defaults=deck_info)
    for card_id, quantity in decklist.slots.items():
        # Skip signature cards/weaknesses
        try:
            card_data = CardInfo.objects.get(card_id=card_id)
            DeckCard.objects.update_or_create(
                deck=deck, card_data=card_data, quantity=quantity
            )
        except CardInfo.DoesNotExist:
            continue

    deck.tags = []
    if decklist.tags and isinstance(decklist.tags, str):
        deck.tags.extend(decklist.tags.split(", "))

    deck.player_count = determine_player_count(
        deck.deck_name, deck.description, deck.tags
    )

    decklist_metadata = retrieve_arkhamdb_decklist_metadata(deck_id)
    deck.comments = decklist_metadata.comments
    deck.favorites = decklist_metadata.favorites
    deck.likes = decklist_metadata.likes

    deck.save()


@router.post("/fetch_latest_decklists")
def fetch_latest_decklists(request) -> None:
    if not (
        newest_decklist := DeckList.objects.all()
        .order_by("arkhamdb_creation_date")
        .last()
    ):
        next_decklist_date = date.fromisoformat(FIRST_ARKHAMDB_DECKLIST_DATE)
    else:
        last_decklist_date = newest_decklist.arkhamdb_creation_date
        next_decklist_date = (
            datetime.combine(last_decklist_date, datetime.min.time())
            + timedelta(days=1)
        ).date()

    while next_decklist_date < date.today():
        new_decklists = retrieve_arkhamdb_decklists_by_date(next_decklist_date)
        for decklist in new_decklists:
            save_decklist_info(decklist)

        next_decklist_date = (
            datetime.combine(next_decklist_date, datetime.min.time())
            + timedelta(days=1)
        ).date()


@router.post("/fetch_decklist/{deck_id}")
def fetch_decklist(request, deck_id: int) -> None:
    decklist = retrieve_arkhamdb_decklist_by_id(deck_id)
    save_decklist_info(decklist)
    # return DeckListSchema(decklist)


@router.post("/fetch_decklist_breakdown", response=dict[str, DeckListBreakdownSchema])
def fetch_decklist_breakdown(
    request, decklists_request: DecklistsRequestSchema
) -> dict[str, DeckListBreakdownSchema]:
    output = dict()
    decklists = DeckList.objects.all()
    if investigator := decklists_request.investigator_name:
        decklists = decklists.filter(investigator_name=investigator)
    decklists = decklists.order_by("deck_id")[
        decklists_request.offset : decklists_request.offset
        + decklists_request.num_entities
    ]
    for decklist in decklists:
        card_presence = dict()
        # card_presence indicates whether each card in card_ids is present in deck_cards
        for card_id in decklists_request.card_ids:
            card_presence[card_id] = decklist.deck_cards.filter(
                card_data__card_id=card_id
            ).exists()
            # if not card_presence[card_id]:
            #     card = CardInfo.objects.filter(card_id=card_id).first()
            #     if (reprint := CardInfo.objects.filter(
            #             name=card.name, subname=card.subname, xp=card.xp
            #         )
            #     ).exists():
            #         reprint = reprint.first()
            #         card_presence[card_id] = decklist.deck_cards.filter(
            #             card_data__card_id=reprint.card_id
            #         ).exists()

        total_xp = decklist.deck_cards.aggregate(
            total_xp=Sum(F("quantity") * F("card_data__xp"))
        )["total_xp"]
        if total_xp is None:
            # log an error with the card_name of the card_data of each DeckCard in deck_cards in decklist
            logging.warning(
                f"Decklist {decklist.deck_id} has no xp: {[deck_card.card_data.name for deck_card in decklist.deck_cards.all()]}"
            )
            continue
        # card_names = [
        #     # f"{deck_card.quantity} X {deck_card.card_data.name}{f' ({deck_card.card_data.xp})' if deck_card.card_data.xp else ''}"
        #     {
        #         "name": f"{deck_card.card_data.name}{f' ({deck_card.card_data.xp})' if deck_card.card_data.xp else ''}",
        #         "quantity": deck_card.quantity,
        #     }
        #     for deck_card in decklist.deck_cards.all()
        # ]
        output[str(decklist.deck_id)] = DeckListBreakdownSchema(
            investigator_name=decklist.investigator_name,
            card_presence=card_presence,
            deck_xp=total_xp,
        )
    return output
