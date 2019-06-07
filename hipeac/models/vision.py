from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils import timezone

from .mixins import LinkMixin


class VisionManager(models.Manager):
    def published(self):
        return self.filter(
            publication_date__lte=timezone.now().date()
        )


class Vision(LinkMixin, models.Model):
    ASSETS_FOLDER = 'public/vision'
    ASSETS_PRIVATE_FOLDER = 'private/vision'

    title = models.CharField(max_length=250)
    introduction = models.TextField(null=True)
    summary = models.TextField(null=True)
    publication_date = models.DateField(default=timezone.now)

    file_draft = models.FileField(upload_to=ASSETS_PRIVATE_FOLDER, null=True, blank=True)
    file = models.FileField(upload_to=ASSETS_PRIVATE_FOLDER, null=True, blank=True)
    flyer = models.FileField(upload_to=ASSETS_FOLDER, null=True, blank=True)
    downloads = models.PositiveSmallIntegerField(default=0)

    images = GenericRelation('hipeac.Image')
    links = GenericRelation('hipeac.Link')
    public_files = GenericRelation('hipeac.PublicFile')

    objects = VisionManager()

    class Meta:
        ordering = ['-publication_date']

    def __str__(self) -> str:
        return self.title

    def get_download_url(self) -> str:
        return reverse('vision_download', args=[self.publication_date.year])
