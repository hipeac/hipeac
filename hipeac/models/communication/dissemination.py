from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django_countries.fields import CountryField

from hipeac.models.mixins import (
    ApplicationAreasMixin,
    FilesMixin,
    ImagesMixin,
    InstitutionsMixin,
    LinksMixin,
    TopicsMixin,
)

from .vars import SECTION_CHOICES


class Dissemination(
    ApplicationAreasMixin, FilesMixin, ImagesMixin, InstitutionsMixin, LinksMixin, TopicsMixin, models.Model
):
    type = models.CharField(max_length=16, null=True, blank=True, choices=SECTION_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    event = models.CharField(max_length=250)
    country = CountryField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "hipeac_comm_dissemination"
        ordering = ("-start_date",)
        verbose_name = "Dissemination event"

    def __str__(self) -> str:
        return f'{self.event} ({self.start_date.strftime("%B %Y")})'

    def get_absolute_url(self) -> str | None:
        if self.type == "roadshow":
            return reverse("roadshow", kwargs={"pk": self.pk, "slug": self.slug})
        return None

    @property
    def name(self) -> str:
        return self.event

    @property
    def slug(self) -> str:
        return slugify(self.event)
