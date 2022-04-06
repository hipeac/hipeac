from django.db import models
from django.urls import reverse
from django.utils import timezone

from ..mixins import ImagesMixin, LinksMixin, FilesMixin, VideosMixin


class VisionQuerySet(models.QuerySet):
    def published(self):
        return self.filter(publication_date__lte=timezone.now().date())


class Vision(ImagesMixin, LinksMixin, FilesMixin, VideosMixin, models.Model):
    ASSETS_FOLDER = "public/vision"
    ASSETS_PRIVATE_FOLDER = "private/vision"

    title = models.CharField(max_length=250)
    introduction = models.TextField(null=True)
    summary = models.TextField(null=True)
    publication_date = models.DateField(default=timezone.now)

    file_draft = models.FileField(upload_to=ASSETS_PRIVATE_FOLDER, null=True, blank=True)
    file = models.FileField(upload_to=ASSETS_PRIVATE_FOLDER, null=True, blank=True)
    flyer = models.FileField(upload_to=ASSETS_FOLDER, null=True, blank=True)
    downloads = models.PositiveIntegerField(default=0)

    objects = VisionQuerySet.as_manager()

    class Meta:
        ordering = ("-publication_date",)
        verbose_name = "Vision document"

    def __str__(self) -> str:
        return self.title

    def get_download_url(self) -> str:
        return reverse("vision_download", args=[self.publication_date.year])


class VisionArticle(models.Model):
    vision = models.ForeignKey(Vision, related_name="articles", on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    authors = models.CharField(max_length=250, null=True, blank=True)
    dimension = models.CharField(max_length=250, null=True, blank=True)
    position = models.PositiveSmallIntegerField()
    abstract = models.TextField(null=True, blank=True)
    downloads = models.PositiveIntegerField(default=0)
    doi_url = models.URLField()

    class Meta:
        db_table = "hipeac_vision_article"
        ordering = ("position",)

    def get_download_url(self) -> str:
        return reverse("vision_article_download", args=[self.vision.publication_date.year, self.id])
