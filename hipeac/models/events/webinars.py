import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from typing import Optional

from .sessions import SessionAbstractModel


class Webinar(SessionAbstractModel):
    event = models.ForeignKey("hipeac.Event", on_delete=models.CASCADE, related_name="webinars", null=True, blank=True)

    zoom_webinar_id = models.CharField(max_length=32, null=True, blank=True)
    zoom_attendee_report = models.FileField(upload_to="private/zoom", null=True, blank=True)

    def get_absolute_url(self) -> str:
        if self.event:
            return "".join([self.event.get_absolute_url(), f"#/webinars/{self.id}/"])
        return f"/webinars/#/{self.id}/"

    @property
    def zoom_webinar_int(self) -> Optional[int]:
        return int(self.zoom_webinar_id.replace(" ", "")) if self.zoom_webinar_id else None


class SessionAccessLink(models.Model):
    session = models.ForeignKey("hipeac.Session", on_delete=models.CASCADE, related_name="access_links")
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.CASCADE, related_name="access_links")
    url = models.URLField(max_length=500)


class WebinarRegistrationQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(webinar__end_at__gte=timezone.now())


class WebinarRegistration(models.Model):
    """
    A webinar registration for a User.
    """

    webinar = models.ForeignKey("hipeac.Webinar", on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(
        get_user_model(), null=True, on_delete=models.CASCADE, related_name="webinar_registrations"
    )
    access_link = models.URLField(max_length=500, null=True, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WebinarRegistrationQuerySet.as_manager()

    class Meta:
        db_table = "hipeac_webinar_registration"
        ordering = ("-created_at",)
        unique_together = ("webinar", "user")
