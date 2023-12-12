from ninja import ModelSchema

from cards.models import CardInfo


class CardInfoSchema(ModelSchema):
    class Config:
        model = CardInfo
        model_fields = "__all__"
