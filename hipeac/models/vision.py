from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone

from .mixins import LinkMixin


class Vision(LinkMixin, models.Model):
    ASSETS_FOLDER = 'public/vision'

    title = models.CharField(max_length=250)
    introduction = models.TextField(null=True)
    summary = models.TextField(null=True)
    publication_date = models.DateField(default=timezone.now)

    file = models.FileField(upload_to=ASSETS_FOLDER, null=True, blank=True)
    file_draft = models.FileField(upload_to=ASSETS_FOLDER, null=True, blank=True)
    downloads = models.PositiveSmallIntegerField(default=0)
    downloads_draft = models.PositiveSmallIntegerField(default=0)

    images = GenericRelation('hipeac.Image')
    links = GenericRelation('hipeac.Link')

    class Meta:
        ordering = ['-publication_date']
