from .base import EventDetail


class CswDetail(EventDetail):
    """Displays a CSW page."""

    template_name = "__v3__/events/csw/csw.html"
