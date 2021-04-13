from .base import EventDetail


class CswDetail(EventDetail):
    """Displays a CSW page.
    """

    template_name = "events/csw/csw.html"
