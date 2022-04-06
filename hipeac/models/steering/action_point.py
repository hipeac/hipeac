from django.db import models
from django.urls import reverse

from hipeac.models.mixins import FilesMixin, UsersMixin


class ActionPointQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status__in=ActionPoint.STATUS_IN_REVIEW)


class ActionPoint(FilesMixin, UsersMixin, models.Model):
    """
    Steering Committee action point.
    """

    STATUS_CHOICES = (
        ("discarded", "Discarded"),
        ("not_started", "Not started"),
        ("in_progress", "In progress"),
        ("completed", "Completed"),
        ("finalized", "Finalized"),
    )
    STATUS_FINALIZED = ("discarded", "finalized")
    STATUS_IN_REVIEW = ("not_started", "in_progress", "completed")

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="UN")
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    progress = models.TextField("Progress description", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = ActionPointQuerySet.as_manager()

    class Meta:
        db_table = "hipeac_steering_action_point"
        ordering = ("-id",)
        verbose_name = "Steering Committee action point"

    def __str__(self) -> str:
        return f"A{self.id}: {self.title}"

    def is_finalized(self) -> bool:
        return self.status == "finalized"

    def get_absolute_url(self) -> str:
        return "".join([reverse("steering"), "#/action-points/"])

    @property
    def owners(self):
        return self.users
