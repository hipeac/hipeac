from .base import EventDetail


class ConferenceDetail(EventDetail):
    """Displays a Conference page."""

    template_name = "events/conference/conference.html"

    def get_object(self, queryset=None):
        if not hasattr(self, "object"):
            self.object = self.get_queryset().get(type="conference", start_date__year=self.kwargs.get("year"))
        return self.object
