from django.db import models
from django.urls import reverse
from django.utils import timezone

from hipeac.models.mixins import (
    ApplicationAreasMixin,
    FilesMixin,
    ImagesMixin,
    InstitutionsMixin,
    LinksMixin,
    ProjectsMixin,
    TopicsMixin,
    UsersMixin,
)


class Magazine(
    ApplicationAreasMixin,
    FilesMixin,
    ImagesMixin,
    InstitutionsMixin,
    LinksMixin,
    ProjectsMixin,
    TopicsMixin,
    UsersMixin,
):
    title = models.CharField(max_length=250)
    publication_date = models.DateField(default=timezone.now)
    file = models.FileField(upload_to="private/magazine", null=True, blank=True)
    issuu_url = models.URLField(null=True, blank=True)
    downloads = models.PositiveSmallIntegerField(default=0)

    event = models.ForeignKey(
        "hipeac.Event", null=True, blank=True, on_delete=models.SET_NULL, related_name="magazines"
    )

    class Meta:
        db_table = "hipeac_comm_magazine"
        ordering = ("-publication_date",)

    def __str__(self) -> str:
        return self.title

    def get_download_url(self) -> str:
        return reverse("magazine_download", args=[self.id])
