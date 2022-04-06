from hipeac.api.serializers.events.conferences import ConferenceSerializer
from hipeac.models import Conference, ConferenceRegistration
from .events import BaseEventViewSet


class ConferenceViewSet(BaseEventViewSet):
    queryset = Conference.objects.all()
    registration_model = ConferenceRegistration
    serializer_class = ConferenceSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "sponsors__institution",
                "sponsors__project",
            )
        )
