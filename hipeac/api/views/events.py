from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from hipeac.models import Event, Roadshow, Session
from ..permissions import HasAdminPermissionOrReadOnly
from ..serializers import (
    EventListSerializer, EventSerializer,
    RoadshowListSerializer, RoadshowSerializer,
    SessionListSerializer, SessionSerializer
)


class EventViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Event.objects.select_related('coordinating_institution')
    serializer_class = EventSerializer

    def list(self, request, *args, **kwargs):
        self.pagination_class = None
        self.serializer_class = EventListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related('sessions', 'sessions__projects')
        return super().retrieve(request, *args, **kwargs)


class RoadshowViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Roadshow.objects.prefetch_related('institutions')
    serializer_class = RoadshowSerializer

    def list(self, request, *args, **kwargs):
        self.pagination_class = None
        self.serializer_class = RoadshowListSerializer
        return super().list(request, *args, **kwargs)


class SessionViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Session.objects.prefetch_related('projects')
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = SessionSerializer
