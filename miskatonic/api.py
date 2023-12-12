from ninja import NinjaAPI
from ninja.security import HttpBearer

from cards.api import router as cards_router
from decks.api import router as decks_router


class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        if token == "supersecretauthtokengiraffe":
            return token


api = NinjaAPI(auth=GlobalAuth())
api.add_router("/cards/", cards_router)
api.add_router("/decks/", decks_router)
