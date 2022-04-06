from django.db import models
from django_countries.fields import CountryField

from hipeac.models.mixins import FilesMixin
from .vars import SECTION_CHOICES


class Dissemination(FilesMixin, models.Model):
    type = models.CharField(max_length=16, null=True, blank=True, choices=SECTION_CHOICES)
    date = models.DateField()
    event = models.CharField(max_length=250)
    country = CountryField(null=True, blank=True)
    description = models.TextField(blank=True)
    external_url = models.URLField(null=True, blank=True)

    class Meta:
        db_table = "hipeac_comm_dissemination"
        ordering = ("-date",)
        verbose_name = "Dissemination event"

    def __str__(self) -> str:
        return f'{self.event} ({self.date.strftime("%B %Y")})'
