from hipeac.models import Conference
from .base import EventDetail


class ConferenceDetail(EventDetail):
    """Displays a Conference page."""

    model = Conference
    template_name = "__v3__/events/conference/conference.html"

    def get_object(self, queryset=None):
        if not hasattr(self, "object"):
            self.object = self.get_queryset().get(type="conference", start_date__year=self.kwargs.get("year"))
        return self.object
