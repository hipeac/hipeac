from django.db import models
from django.template.defaultfilters import slugify
from django_countries.fields import CountryField

from .mixins import ImagesMixin, InstitutionsMixin, LinksMixin


class Roadshow(ImagesMixin, InstitutionsMixin, LinksMixin, models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    name = models.CharField(max_length=250)
    description = models.TextField("Presentation")
    country = CountryField()

    class Meta:
        ordering = ("-start_date",)

    def __str__(self) -> str:
        return f'{self.name} ({self.start_date.strftime("%B %Y")})'

    @property
    def slug(self) -> str:
        return slugify(self.name)
