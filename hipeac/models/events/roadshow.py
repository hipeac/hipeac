from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django_countries.fields import CountryField

from ..mixins import UrlMixin


class Roadshow(UrlMixin, models.Model):
    route_name = 'roadshow'

    start_date = models.DateField()
    end_date = models.DateField()

    name = models.CharField(max_length=250)
    description = models.TextField('Presentation')
    country = CountryField()
    institutions = models.ManyToManyField('hipeac.Institution', blank=True, related_name='roadshow_events',
                                          help_text='Optionally, indicate institutions that will attend the event.')

    images = GenericRelation('hipeac.Image')
    links = GenericRelation('hipeac.Link')

    class Meta(object):
        ordering = ['start_date']

    def __str__(self) -> str:
        return f'{self.name} ({self.start_date.strftime("%B %Y")})'

    @property
    def slug(self) -> str:
        return slugify(self.name)
