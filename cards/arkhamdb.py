from string import Template
from logging import getLogger

import requests
from requests.exceptions import RequestException
from pydantic import ValidationError, root_validator, Field
from ninja import Schema

from exceptions import CardDataRetrievalError
from constants import Faction, Skill, PlayerCardType

logger = getLogger(__name__)

ARKHAMDB_CARD_INFO_API = Template("https://arkhamdb.com/api/public/card/$card_code")
ARKHAMDB_ALL_CARDS_API = "https://arkhamdb.com/api/public/cards"


class ArkhamDBCardInfoResponse(Schema):
    name: str
    subname: str | None
    pack_name: str
    type_name: str
    subtype_name: str | None
    factions: list[Faction]
    exceptional: bool
    myriad: bool
    card_id: str = Field(..., alias="code")
    cost: int | None
    text: str | None
    skills: dict[Skill, int] | None
    xp: int | None
    deck_limit: int | None
    traits: list[str] | None
    is_unique: bool
    permanent: bool
    octgn_id: str | None
    url: str
    imagesrc: str | None
    restrictions: dict | None = Field(default_factory=dict)

    class Config:
        json_encoders = {list: lambda s: sorted(list(s))}
        allow_population_by_field_name = True

    #     fields = {"value": ""}

    @root_validator(pre=True)
    def set_skills(cls, values):
        values["skills"] = {}
        logger.debug(f"values: {values}")
        for skill, skill_field_name in [
            (skill.value, f"skill_{skill}") for skill in Skill
        ]:
            values["skills"][skill] = values.get(skill_field_name, 0)

        return values

    @root_validator(pre=True)
    def set_traits(cls, values):
        if isinstance((traits := values.get("traits", "")), str) is False:
            raise ValueError(
                f"traits field {traits} is of type {type(traits)} and not a subclass of str"
            )
        values["traits"] = list(
            map(lambda trait: trait.replace(".", "").lower(), traits.split())
        )
        return values

    @root_validator(pre=True)
    def set_factions(cls, values):
        values["factions"] = []
        for faction_field_name in [
            "faction_code",
            "faction1_code",
            "faction2_code",
            "faction3_code",
        ]:
            if faction_code := values.get(faction_field_name):
                # Only player cards should end up here
                if faction_code == Faction.MYTHOS:
                    raise ValueError(f"Unexpected encounter card received: {values}")
                values["factions"].append(Faction(faction_code))
        return values


class ArkhamDBCardInfoSchema(Schema):
    pass


def retrieve_card_info_from_arkhamdb(card_id: str) -> ArkhamDBCardInfoResponse:
    try:
        response = requests.get(ARKHAMDB_CARD_INFO_API.substitute(card_code=card_id))
    except RequestException as exc:
        raise CardDataRetrievalError(
            f"Failed to retrieve card info from API: {exc}"
        ) from exc
    if not response.ok:
        raise CardDataRetrievalError(
            f"Failed to retrieve card info from API with status code: {response.status_code}"
        )
    logger.info(f"Response length: {len(response.json())}")
    try:
        return ArkhamDBCardInfoResponse(**response.json())
    except ValidationError as exc:
        raise CardDataRetrievalError(
            f"Failed to validate response from card data retrieval API: {response.json()}"
        ) from exc


def retrieve_all_card_info_from_arkhamdb() -> list[ArkhamDBCardInfoResponse]:
    try:
        response = requests.get(
            ARKHAMDB_ALL_CARDS_API, {"_format": "json", "encounter": 0}
        )
        logger.info(f"Response length: {len(response.json())}")
        if not response.ok:
            raise CardDataRetrievalError(
                f"Failed to retrieve card info from API for all cards with status code: {response.status_code}"
            )
    except RequestException as exc:
        raise CardDataRetrievalError(
            "Failed to retrieve card info from API for all cards"
        ) from exc

    results = []
    player_card_types = list(PlayerCardType)
    for card_info in response.json():
        try:
            if card_info.get("type_code") not in player_card_types and card_info.get(
                "subtype_code"
            ) not in ("basicweakness", "weakness"):
                logger.debug(
                    f"Skipping card {card_info['name']} as it is not a player card"
                )
                continue

            try:
                card = ArkhamDBCardInfoResponse(**card_info)
                logger.debug(f"Card info: {card}")
            except ValidationError as exc:
                logger.exception("Failed to validate card info result")
                raise CardDataRetrievalError(
                    f"Failed to validate card info result: {card_info}"
                ) from exc

            # if card.restrictions:
            #     logger.debug(f"Skipping card {card.name} as it is restricted")
            #     continue

            results.append(card)
        except ValueError:
            logger.exception("Failed to parse card info result")
            raise
        except Exception as exc:
            logger.exception("Unexpected error while parsing card info")
            raise Exception from exc
    logger.info(f"Retrieved {len(results)} cards from ArkhamDB")
    return results
