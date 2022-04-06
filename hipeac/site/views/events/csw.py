from hipeac.models import Csw
from .base import EventDetail


class CswDetail(EventDetail):
    """Displays a CSW page."""

    model = Csw
    template_name = "__v3__/events/csw/csw.html"
