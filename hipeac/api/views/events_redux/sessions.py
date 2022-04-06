from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.parsers import FileUploadParser
from rest_framework.viewsets import GenericViewSet

from hipeac.models import AcacesRegistration, Event, Session
from ...permissions import HasAdminPermissionOrReadOnly, HasRegistrationForRelatedEvent
from ...serializers import RegistrationListSerializer, SessionListSerializer, SessionSerializer, VideoListSerializer


class SessionViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Session.objects.all()
    pagination_class = None
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = SessionSerializer

    def list(self, request, *args, **kwargs):
        self.serializer_class = SessionListSerializer
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        permission_classes=(HasRegistrationForRelatedEvent,),
        serializer_class=RegistrationListSerializer,
    )
    def attendees(self, request, *args, **kwargs):
        session = self.get_object()
        self.queryset = session.registrations.select_related("user__profile").prefetch_related(
            "user__profile__institution"
        )

        if session.event.type == Event.ACACES:
            self.queryset = self.queryset.filter(
                acacesregistration__status=AcacesRegistration.STATUS_ADMITTED, acacesregistration__accepted=True
            )

        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = self.get_object().videos
        return super().list(request, *args, **kwargs)
