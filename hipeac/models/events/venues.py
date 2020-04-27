from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django_countries.fields import CountryField


class Venue(models.Model):
    name = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    country = CountryField()
    description = models.TextField(null=True, blank=True)

    images = GenericRelation("hipeac.Image")
    links = GenericRelation("hipeac.Link")

    def __str__(self) -> str:
        return f"{self.name} ({self.city}, {self.country})"


class Room(models.Model):
    venue = models.ForeignKey(Venue, related_name="rooms", on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta(object):
        ordering = ["position"]

    def __str__(self):
        return f"{self.venue} - Room: {self.name}"
