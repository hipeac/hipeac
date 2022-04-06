from django.db import models
from django_countries.fields import CountryField

from ..mixins import LinksMixin


class Venue(LinksMixin, models.Model):
    name = models.CharField(max_length=160)
    city = models.CharField(max_length=160, null=True, blank=True)
    country = CountryField(db_index=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "hipeac_event_venue"
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} ({self.city})"


class Room(models.Model):
    venue = models.ForeignKey(Venue, related_name="rooms", on_delete=models.CASCADE)
    name = models.CharField(max_length=190)
    max_capacity = models.PositiveSmallIntegerField(default=0)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "hipeac_event_venue_room"
        ordering = ("position",)

    def __str__(self) -> str:
        return f"{self.venue} - Room: {self.name}"
