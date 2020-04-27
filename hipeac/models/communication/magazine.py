from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.urls import reverse
from django.utils import timezone

from ..mixins import LinkMixin


class Magazine(LinkMixin, models.Model):
    ASSETS_FOLDER = "public/magazine"
    ASSETS_PRIVATE_FOLDER = "private/magazine"

    title = models.CharField(max_length=250)
    publication_date = models.DateField(default=timezone.now)
    file = models.FileField(upload_to=ASSETS_PRIVATE_FOLDER, null=True, blank=True)
    file_tablet = models.FileField(upload_to=ASSETS_PRIVATE_FOLDER, null=True, blank=True)
    issuu_url = models.URLField(null=True, blank=True)
    downloads = models.PositiveSmallIntegerField(default=0)

    event = models.ForeignKey(
        "hipeac.Event", null=True, blank=True, on_delete=models.SET_NULL, related_name="magazines"
    )
    application_areas = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    projects = models.ManyToManyField("hipeac.Project", blank=True, related_name="magazines")
    users = models.ManyToManyField(get_user_model(), blank=True, related_name="magazines")
    images = GenericRelation("hipeac.Image")

    class Meta:
        ordering = ["-publication_date"]

    def __str__(self) -> str:
        return self.title

    def get_download_url(self) -> str:
        return reverse("magazine_download", args=[self.id])
