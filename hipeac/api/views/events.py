from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Event, Roadshow, Session
from ..permissions import HasAdminPermissionOrReadOnly, HasRegistrationForEvent
from ..serializers import (
    ArticleListSerializer,
    EventListSerializer, EventSerializer,
    RegistrationListSerializer,
    RoadshowListSerializer, RoadshowSerializer,
    SessionListSerializer, SessionSerializer
)


class EventViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Event.objects.public().select_related('coordinating_institution')
    serializer_class = EventSerializer

    def list(self, request, *args, **kwargs):
        self.pagination_class = None
        self.serializer_class = EventListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related('sessions', 'sessions__projects')
        return super().retrieve(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=ArticleListSerializer,
    )
    def articles(self, request, *args, **kwargs):
        self.queryset = self.get_object().articles.prefetch_related('institutions', 'projects')
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        permission_classes=(HasRegistrationForEvent,),
        serializer_class=RegistrationListSerializer,
    )
    def registrations(self, request, *args, **kwargs):
        self.queryset = self.get_object().registrations \
                            .select_related('user__profile') \
                            .prefetch_related('user__profile__institution', 'user__profile__second_institution') \
                            .prefetch_related('user__profile__projects')

        return super().list(request, *args, **kwargs)


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

    def list(self, request, *args, **kwargs):
        self.pagination_class = None
        self.serializer_class = SessionListSerializer
        return super().list(request, *args, **kwargs)
