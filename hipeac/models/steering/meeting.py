from django.db import models
from django.urls import reverse

from ..mixins import FilesMixin


class Meeting(FilesMixin, models.Model):
    """
    Steering Committee meeting.
    """

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    location = models.CharField(max_length=250)
    description = models.TextField()
    url_webex = models.URLField(null=True, blank=True)
    minutes = models.FileField(upload_to="private/steering/meeting", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hipeac_steering_meeting"
        ordering = ("-start_at",)
        verbose_name = "Steering Committee meeting"

    def get_absolute_url(self) -> str:
        return "".join([reverse("steering"), f"#/meetings/{self.id}/"])
