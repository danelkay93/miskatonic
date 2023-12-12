from django.contrib.postgres.fields import ArrayField
from django.db import models

from django_extensions.db.models import TimeStampedModel

from constants import Faction


class CardInfo(TimeStampedModel):
    name = models.CharField(blank=False, null=False, max_length=64)
    subname = models.CharField(blank=True, null=True, max_length=64)
    pack_name = models.CharField(blank=False, null=False, max_length=64)
    type_name = models.CharField(blank=False, null=False, max_length=64)
    subtype_name = models.CharField(blank=True, null=True, max_length=64)
    factions = ArrayField(
        models.CharField(
            max_length=64,
            choices=models.TextChoices(
                "Factions", " ".join([faction_name.upper() for faction_name in Faction])
            ).choices,
        ),
        default=list,
    )
    exceptional = models.BooleanField(blank=False, null=False)
    myriad = models.BooleanField(blank=False, null=False)
    card_id: str = models.CharField(
        primary_key=True, blank=False, null=False, max_length=32
    )
    cost = models.IntegerField(blank=True, null=True)
    text = models.TextField(blank=True, null=True, max_length=1024)
    skills = models.JSONField(
        default=dict,
        # base_field=models.CharField(
        #     max_length=64,
        #     choices=models.TextChoices(
        #         "Skills", "".join([skill_name.upper() for skill_name in Skill])
        #     ).choices,
        blank=False,
        null=False,
    )
    xp = models.IntegerField(blank=True, null=True)
    deck_limit = models.IntegerField(blank=True, null=True)
    traits = ArrayField(
        base_field=models.CharField(max_length=64),
        default=list,
    )
    is_unique = models.BooleanField(blank=False, null=False)
    permanent = models.BooleanField(blank=False, null=False)
    octgn_id = models.CharField(blank=True, null=True, max_length=64)
    url = models.CharField(blank=False, null=False, max_length=256)
    imagesrc = models.CharField(blank=True, null=True, max_length=256)
    restrictions = models.JSONField(default=dict, blank=False, null=False)
