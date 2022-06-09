from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin

from hipeac.api.serializers.events.conferences import ConferenceSerializer
from hipeac.models import Conference, ConferenceRegistration
from .events import BaseEventViewSet
from ...serializers import JobNestedSerializer


class ConferenceViewSet(BaseEventViewSet):
    queryset = Conference.objects.all()
    registration_model = ConferenceRegistration
    serializer_class = ConferenceSerializer

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=JobNestedSerializer,
    )
    def jobs(self, request, *args, **kwargs):
        self.queryset = self.get_object().jobs
        return super().list(request, *args, **kwargs)
