from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse


class ActionPointQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status__in=ActionPoint.STATUS_IN_REVIEW)


class ActionPoint(models.Model):
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

    owners = models.ManyToManyField(get_user_model(), related_name="action_points")
    attachments = GenericRelation("hipeac.PrivateFile")

    objects = ActionPointQuerySet.as_manager()

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"A{self.id}: {self.title}"

    def is_finalized(self) -> bool:
        return self.status == "FI"

    def get_absolute_url(self) -> str:
        return "".join([reverse("steering"), f"#/action-points/"])
