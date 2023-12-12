from ninja import Router

from cards.arkhamdb import (
    retrieve_card_info_from_arkhamdb,
    retrieve_all_card_info_from_arkhamdb,
)
from cards.models import CardInfo
from cards.schemas import CardInfoSchema

router = Router()


@router.get("/card_info/{card_id}", response=CardInfoSchema)
def card_info(request, card_id: str):
    try:
        return CardInfo.objects.get(card_id=card_id)
    except CardInfo.DoesNotExist:
        card_info = retrieve_card_info_from_arkhamdb(card_id).dict(by_alias=False)
        card_info.pop("card_id")
        return CardInfo.objects.create(
            card_id=card_id,
            **card_info,
        )


@router.post("/fetch_cards", response=list[CardInfoSchema])
def fetch_cards(request) -> list[CardInfoSchema]:
    results = []
    cards = retrieve_all_card_info_from_arkhamdb()
    for card_info in cards:
        card_info = card_info.dict(by_alias=False)
        card_id = card_info.pop("card_id")
        card, _ = CardInfo.objects.get_or_create(card_id=card_id, defaults=card_info)
        results.append(card)
    return results
