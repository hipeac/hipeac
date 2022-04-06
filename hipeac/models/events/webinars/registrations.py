from django.db import models
from django.utils import timezone

from ..registrations import RegistrationAbstractModel


class WebinarRegistrationQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(webinar__end_at__gte=timezone.now())


class WebinarRegistration(RegistrationAbstractModel):
    webinar = models.ForeignKey("hipeac.Webinar", related_name="registrations", on_delete=models.CASCADE)
    zoom_access_link = models.URLField(max_length=500)

    objects = WebinarRegistrationQuerySet.as_manager()

    class Meta:
        db_table = "hipeac_webinar_registration"
        unique_together = ("webinar", "user")
