from django.contrib.auth import get_user_model
from django.db import models

from .vars import SECTION_CHOICES


class Quote(models.Model):
    type = models.CharField(max_length=16, null=True, blank=True, choices=SECTION_CHOICES)
    text = models.TextField()
    author = models.CharField(max_length=250)
    institution = models.ForeignKey(
        "hipeac.Institution", related_name="quotes", null=True, blank=True, on_delete=models.SET_NULL
    )
    user = models.ForeignKey(get_user_model(), related_name="quotes", null=True, blank=True, on_delete=models.SET_NULL)
    is_featured = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["type"]),
        ]

    def __str__(self) -> str:
        return f"Quote: {self.type} ({self.author})"
