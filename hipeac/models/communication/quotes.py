from django.db import models

from hipeac.models.mixins import InstitutionsMixin, ProjectsMixin, UsersMixin
from .vars import SECTION_CHOICES


class QuoteManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "rel_institutions__institution",
                "rel_projects__project",
                "rel_users__user__profile",
            )
        )


class Quote(InstitutionsMixin, ProjectsMixin, UsersMixin, models.Model):
    type = models.CharField(max_length=16, null=True, blank=True, choices=SECTION_CHOICES)
    text = models.TextField()
    author = models.CharField(max_length=250)
    is_featured = models.BooleanField(default=False)

    objects = QuoteManager()

    class Meta:
        db_table = "hipeac_comm_quote"
        indexes = [models.Index(fields=["type"])]

    def __str__(self) -> str:
        return f"Quote: {self.type} ({self.author})"
