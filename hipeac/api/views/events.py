from django.db import IntegrityError
from django.db.models import Q
from django.views.decorators.cache import never_cache
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Job, Event, Roadshow, Session, Registration
from ..permissions import HasAdminPermissionOrReadOnly, HasRegistrationForEvent, RegistrationPermission
from ..serializers import (
    ArticleListSerializer,
    EventListSerializer, EventSerializer,
    JobNestedSerializer,
    RegistrationListSerializer, AuthRegistrationSerializer,
    RoadshowListSerializer, RoadshowSerializer,
    SessionListSerializer, SessionSerializer
)


class EventViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Event.objects.public().select_related('coordinating_institution').prefetch_related('links')
    serializer_class = EventSerializer

    def list(self, request, *args, **kwargs):
        self.pagination_class = None
        self.serializer_class = EventListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related('sponsors', 'sessions__links', 'sessions__projects')
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
        serializer_class=JobNestedSerializer,
    )
    def jobs(self, request, *args, **kwargs):
        sponsors = self.get_object().sponsors.values_list('institution_id', 'project_id')
        if sponsors:
            a, b = map(list, zip(*sponsors))
            institution_ids, project_ids = list(filter(None, a)), list(filter(None, b))
            self.queryset = Job.objects.active().filter(
                (Q(institution__in=institution_ids) | Q(project__in=project_ids)),
            )
        else:
            self.queryset = Job.objects.none()
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
    queryset = Session.objects.prefetch_related('session_type', 'projects')
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = SessionSerializer

    def list(self, request, *args, **kwargs):
        self.pagination_class = None
        self.serializer_class = SessionListSerializer
        return super().list(request, *args, **kwargs)


class RegistrationViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = (RegistrationPermission,)
    serializer_class = AuthRegistrationSerializer

    def get_queryset(self):
        event_id = self.request.query_params.get('event_id', None)
        queryset = Registration.objects.filter(user_id=self.request.user.id).prefetch_related('sessions', 'posters')
        if event_id is not None:
            queryset = queryset.filter(event_id=event_id)
        return queryset

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({'event-user': ['Duplicate entry - this user already has a registration.']})

    @never_cache
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @never_cache
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
