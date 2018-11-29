from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone

from ..mixins import LinkMixin


class Magazine(LinkMixin, models.Model):
    ASSETS_FOLDER = 'public/magazine'

    title = models.CharField(max_length=250)
    publication_date = models.DateField(default=timezone.now)
    file = models.FileField(upload_to=ASSETS_FOLDER, null=True, blank=True)
    file_tablet = models.FileField(upload_to=ASSETS_FOLDER, null=True, blank=True)
    issuu_url = models.URLField(null=True, blank=True)

    images = GenericRelation('hipeac.Image')

    class Meta:
        ordering = ['-publication_date']

    def __str__(self) -> str:
        return self.title
