from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django_countries.fields import CountryField

from .vars import SECTION_CHOICES
from ..mixins import UrlMixin


class Dissemination(UrlMixin, models.Model):
    type = models.CharField(max_length=16, null=True, blank=True, choices=SECTION_CHOICES)
    date = models.DateField()
    event = models.CharField(max_length=250)
    country = CountryField(null=True, blank=True)
    description = models.TextField(blank=True)
    external_url = models.URLField(null=True, blank=True)

    public_files = GenericRelation("hipeac.PublicFile")

    class Meta:
        ordering = ["-date"]
        verbose_name = "Dissemination event"

    def __str__(self) -> str:
        return f'{self.event} ({self.date.strftime("%B %Y")})'
