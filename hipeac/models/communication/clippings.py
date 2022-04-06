from django.db import models
from django.utils import timezone

from .vars import SECTION_CHOICES


class Clipping(models.Model):
    type = models.CharField(max_length=16, null=True, blank=True, choices=SECTION_CHOICES)
    media = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    url = models.URLField()
    publication_date = models.DateField(default=timezone.now)

    class Meta:
        db_table = "hipeac_comm_clipping"
        ordering = ("-publication_date",)

    def __str__(self) -> str:
        return f"Clipping @ {self.media}: {self.title}"
