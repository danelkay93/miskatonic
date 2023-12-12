from django.urls import path

from cards.api import api

app_name = "cards"

urlpatterns = [
    path("", api.urls),
]
