from django.utils import timezone

from ..sessions import SessionAbstractModel


class Webinar(SessionAbstractModel):
    class Meta:
        db_table = "hipeac_webinar"
        ordering = ["start_at"]

    def is_open_for_registration(self) -> bool:
        return (timezone.now() <= self.start_at) and self.zoom_webinar_id is not None
