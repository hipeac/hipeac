from hipeac.api.serializers.events.csw import CswSerializer
from hipeac.models import Csw, CswRegistration
from .events import BaseEventViewSet


class CswViewSet(BaseEventViewSet):
    queryset = Csw.objects.all()
    registration_model = CswRegistration
    serializer_class = CswSerializer
