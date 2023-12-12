import re
from functools import lru_cache
from string import Template
from logging import getLogger
from typing import Any

import requests
from requests.exceptions import RequestException
from pydantic import ValidationError, Field, validator, parse_obj_as
from ninja import Schema
from bs4 import BeautifulSoup

from datetime import date, datetime

from exceptions import (
    DecklistRetrievalError,
    DeckDetailsRetrievalError,
    UserInfoRetrievalError,
)

logger = getLogger(__name__)

ARKHAMDB_DECKLISTS_BY_DATE_API = Template(
    "https://arkhamdb.com/api/public/decklists/by_date/$date.json"
)
ARKHAMDB_DECKLIST_BY_ID_API = Template(
    "https://arkhamdb.com/api/public/decklist/$deck_id.json"
)
ARKHAMDB_DECK_URL = Template("https://arkhamdb.com/decklist/view/$deck_id")
ARKHAMDB_USER_URL = Template("https://arkhamdb.com/user/profile/$user_id/$username")


class ArkhamDBDecklistResponse(Schema):
    deck_id: int = Field(..., alias="id")
    deck_name: str = Field(..., alias="name")
    # date_creation: str = Field(..., alias="date_creation")
    arkhamdb_creation_date: str = Field(..., alias="date_creation")
    arkhamdb_update_date: str = Field(..., alias="date_update")
    description: str = Field(..., alias="description_md")
    user_id: int
    investigator_code: str
    investigator_name: str
    slots: dict[str, int] = Field(..., exclude=True)
    sideSlots: dict[str, int] = Field(..., exclude=True)
    ignoreDeckLimitSlots: Any | None = Field(default=None, exclude=True)
    version: str = Field(..., exclude=True)
    xp: int | None = Field(..., exclude=True)
    xp_spent: int | None = Field(..., exclude=True)
    xp_adjustment: int | None = Field(..., exclude=True)
    exile_string: Any = Field(..., exclude=True)
    taboo_id: Any = Field(..., exclude=True)
    meta: str = Field(..., exclude=True)
    tags: str = Field(..., exclude=True)
    previous_deck: Any = Field(..., exclude=True)
    next_deck: Any = Field(..., exclude=True)

    class Config:
        #     json_encoders = {list: lambda s: sorted(list(s))}
        allow_population_by_field_name = True

    @validator("arkhamdb_creation_date", pre=True)
    def truncate_time_creation(cls, value):
        dt = datetime.fromisoformat(value)
        return dt.date().isoformat()

    @validator("arkhamdb_update_date", pre=True)
    def truncate_time_update(cls, value):
        dt = datetime.fromisoformat(value)
        return dt.date().isoformat()


class ArkhamDBCardInfoSchema(Schema):
    pass


class ArkhamDBDecklistMetaData(Schema):
    likes: int
    favorites: int
    comments: int
    # exp_required: int
    # author_decks: int
    # author_reviews: int
    # author_rep: int
    # author_join_date: date


def retrieve_arkhamdb_decklists_by_date(date: date) -> list[ArkhamDBDecklistResponse]:
    try:
        response = requests.get(
            ARKHAMDB_DECKLISTS_BY_DATE_API.substitute(date=date.isoformat())
        )
    except RequestException as exc:
        raise DecklistRetrievalError(
            f"Failed to retrieve decklist info from API: {exc}"
        ) from exc
    # No decks found
    if response.status_code == 500:
        return []
    elif not response.ok:
        raise DecklistRetrievalError(
            f"Failed to retrieve decklist info from API with status code: {response.status_code}"
        )
    try:
        return parse_obj_as(list[ArkhamDBDecklistResponse], response.json())
    except ValidationError as exc:
        raise DecklistRetrievalError(
            f"Failed to validate response from decklist retrieval API: {response.json()}"
        ) from exc


def retrieve_arkhamdb_decklist_by_id(deck_id: int) -> ArkhamDBDecklistResponse:
    try:
        response = requests.get(ARKHAMDB_DECKLIST_BY_ID_API.substitute(deck_id=deck_id))
    except RequestException as exc:
        raise DecklistRetrievalError(
            f"Failed to retrieve decklist info from API: {exc}"
        ) from exc
    if response.status_code == 500:
        raise DecklistRetrievalError(
            f"Failed to retrieve decklist info from API, decklist not found: {deck_id}"
        )
    elif not response.ok:
        raise DecklistRetrievalError(
            f"Failed to retrieve decklist info from API with status code: {response.status_code}"
        )
    try:
        return ArkhamDBDecklistResponse(**response.json())
    except ValidationError as exc:
        raise DecklistRetrievalError(
            f"Failed to validate response from decklist retrieval API: {response.json()}"
        ) from exc


@lru_cache(maxsize=100024)
def retrieve_arkhamdb_user_data(user_id: str, username: str):
    try:
        response = requests.get(
            ARKHAMDB_USER_URL.substitute(user_id=user_id, username=username)
        )
    except RequestException as exc:
        raise UserInfoRetrievalError(
            f"Failed to retrieve user info from webpage: {exc}"
        ) from exc
    if not response.ok:
        raise UserInfoRetrievalError(
            f"Failed to retrieve user info from webpage with status code: {response.status_code}"
        )
    if not response.text:
        raise UserInfoRetrievalError(
            f"Failed to retrieve user from webpage, page is empty: {response.status_code}"
        )

    soup = BeautifulSoup(response.text, "html.parser")
    soup = soup.select("div", class_="main white container")[0]


@lru_cache(maxsize=100000)
def retrieve_arkhamdb_decklist_metadata(deck_id: int) -> ArkhamDBDecklistMetaData:
    try:
        response = requests.get(ARKHAMDB_DECK_URL.substitute(deck_id=deck_id))
    except RequestException as exc:
        raise DeckDetailsRetrievalError(
            f"Failed to retrieve decklist info from webpage: {exc}"
        ) from exc
    if not response.ok:
        raise DeckDetailsRetrievalError(
            f"Failed to retrieve deck detail info from webpage with status code: {response.status_code}"
        )
    if not response.text:
        raise DeckDetailsRetrievalError(
            f"Failed to retrieve deck detail info from webpage, page is empty: {response.status_code}"
        )

    soup = BeautifulSoup(response.text, "html.parser")
    if not (social_icons := soup.find("span", class_="social-icons")):
        raise DeckDetailsRetrievalError("Failed to retrieve deck metadata")

    def _get_count(elem) -> int:
        if not elem:
            return 0
        num = elem.find("span", class_="num")
        if not num:
            logger.error("Metadata count not found")
            return 0
        return int(num.string)

    likes = _get_count(social_icons.find("a", id="social-icon-like"))
    favorites = _get_count(social_icons.find("a", id="social-icon-favorite"))
    comments = _get_count(social_icons.find("a", id="social-icon-comments"))

    author_profile_url = soup.find("a", class_="username")["href"]
    author_details = re.match(r"\/user\/profile\/([0-9]+)\/(.+)", author_profile_url)
    author_details[1]
    author_details[2]
    # retrieve_arkhamdb_user_data(author_id, author_username)
    return ArkhamDBDecklistMetaData(likes=likes, favorites=favorites, comments=comments)
