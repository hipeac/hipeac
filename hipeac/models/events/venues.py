from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django_countries.fields import CountryField


class Venue(models.Model):
    name = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    country = CountryField()
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    images = GenericRelation('hipeac.Image')

    def __str__(self) -> str:
        return f'{self.name} ({self.city}, {self.country})'
