import json

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import pgettext_lazy


class NotificationQuerySet(models.QuerySet):
    def active(self):
        return self.filter(Q(deadline__gt=timezone.now()) | Q(deadline__isnull=True))


class Notification(models.Model):
    user = models.ForeignKey(get_user_model(), related_name="notifications", null=True, on_delete=models.CASCADE)
    category = models.CharField(pgettext_lazy("-- admin: labels", "category"), db_index=True, max_length=32)
    object_id = models.PositiveIntegerField(null=True)
    value = models.TextField(pgettext_lazy("-- admin: labels", "value"))
    deadline = models.DateTimeField(pgettext_lazy("-- admin: labels", "deadline"), null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["category", "user", "object_id"]),
        ]
        verbose_name = pgettext_lazy("-- admin: notification.verbose_name", "notification")
        verbose_name_plural = pgettext_lazy("-- admin: notification.verbose_name_plural", "notifications")

    def __str__(self) -> str:
        return f"{self.user_id}: {self.category}"

    @property
    def data(self) -> dict:
        return json.loads(self.value)
