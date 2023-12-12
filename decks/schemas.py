from ninja import ModelSchema, Schema

from decks.models import DeckList


class DeckListSchema(ModelSchema):
    class Config:
        model = DeckList
        model_fields = "__all__"


class DeckListBreakdownSchema(Schema):
    investigator_name: str
    card_presence: dict[str, bool]
    deck_xp: int


class DecklistsRequestSchema(Schema):
    investigator_name: str | None
    card_ids: list[str]
    num_entities: int
    offset: int
