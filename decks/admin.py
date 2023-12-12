from django.contrib import admin

from decks.models import DeckList, DeckCard

# Register your models here.
admin.site.register(DeckList)
admin.site.register(DeckCard)
