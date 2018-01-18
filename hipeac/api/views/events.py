from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from hipeac.models import Event, Session
from ..serializers import EventListSerializer, EventSerializer, SessionListSerializer, SessionSerializer


class EventViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Event.objects.select_related('coordinating_institution')

    def list(self, request, *args, **kwargs):
        self.pagination_class = None
        self.serializer_class = EventListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related('sessions', 'sessions__projects')
        self.serializer_class = EventSerializer
        return super().retrieve(request, *args, **kwargs)


class SessionViewSet(ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    def list(self, request, *args, **kwargs):
        self.serializer_class = SessionListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related('projects')
        return super().retrieve(request, *args, **kwargs)
