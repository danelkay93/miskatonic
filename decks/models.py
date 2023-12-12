from django.contrib.postgres.fields import ArrayField
from django.db import models

from django_extensions.db.models import TimeStampedModel

from cards.models import CardInfo
from constants import DeckTag, PlayerCounts


# class Investigator(TimeStampedModel):
#     code = models.CharField(max_length=255, blank=False, null=False, primary_key=True)
#     name = models.CharField(max_length=255, blank=False, null=False)
#     main_faction = models.CharField(max_length=255, blank=False, null=False, choices=models.TextChoices("Factions", " ".join([faction_name.upper() for faction_name in DeckTag])).choices)
#     factions = ArrayField(
#         models.CharField(
#             max_length=64,
#             choices=models.TextChoices(
#                 "Factions", " ".join([faction_name.upper() for faction_name in DeckTag])
#             ).choices,
#         ),
#         default=list,
#     )
#


class DeckList(TimeStampedModel):
    # cards = models.JSONField(default=list, null=False, blank=True)
    deck_id = models.IntegerField(null=False, blank=False, primary_key=True)
    deck_name = models.CharField(max_length=255, blank=False, null=False, default="")
    arkhamdb_creation_date = models.DateField(null=False, blank=False)
    arkhamdb_update_date = models.DateField(null=False, blank=False)
    description = models.TextField()
    user_id = models.IntegerField()
    investigator_code = models.CharField(max_length=255)
    investigator_name = models.CharField(max_length=255)
    likes = models.IntegerField(blank=True, null=True)
    favorites = models.IntegerField(blank=True, null=True)
    comments = models.IntegerField(blank=True, null=True)
    tags = ArrayField(
        models.CharField(
            max_length=64,
            choices=models.TextChoices(
                "Factions", " ".join([faction_name.upper() for faction_name in DeckTag])
            ).choices,
        ),
        default=list,
    )
    player_count = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        choices=models.TextChoices(
            "PlayerCounts",
            " ".join([player_count.upper() for player_count in PlayerCounts]),
        ).choices,
    )


class DeckCard(TimeStampedModel):
    deck = models.ForeignKey(
        DeckList,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="deck_cards",
    )
    card_data = models.ForeignKey(
        CardInfo, on_delete=models.PROTECT, blank=False, null=False
    )
    quantity = models.IntegerField()
