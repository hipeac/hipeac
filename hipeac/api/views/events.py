from django.db import IntegrityError
from django.views.decorators.cache import never_cache
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Event, Roadshow, Session, Registration
from ..permissions import HasAdminPermissionOrReadOnly, HasRegistrationForEvent, RegistrationPermission
from ..serializers import (
    ArticleListSerializer,
    CommitteeListSerializer,
    EventListSerializer, EventSerializer,
    JobNestedSerializer,
    RegistrationListSerializer, AuthRegistrationSerializer,
    RoadshowListSerializer, RoadshowSerializer,
    SessionListSerializer, SessionSerializer,
    VideoListSerializer
)


class EventViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Event.objects.public()
    serializer_class = EventSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer('travel_info')
        self.pagination_class = None
        self.serializer_class = EventListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.select_related('coordinating_institution') \
                                     .prefetch_related('breaks', 'fees', 'links',
                                                       'venues__rooms',
                                                       'sponsors__institution', 'sponsors__project',
                                                       'sessions__session_type')
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
        serializer_class=CommitteeListSerializer,
    )
    def committees(self, request, *args, **kwargs):
        self.queryset = self.get_object().committees.prefetch_related('members__profile__institution')
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=JobNestedSerializer,
    )
    def jobs(self, request, *args, **kwargs):
        self.queryset = self.get_object().jobs
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

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=SessionSerializer,
    )
    def sessions(self, request, *args, **kwargs):
        session_type = request.query_params.get('session_type', False)
        if not session_type:
            raise PermissionDenied('Please include a `session_type` query parameter in your request.')

        self.queryset = self.get_object().sessions.filter(session_type=session_type) \
                                                  .prefetch_related('session_type', 'main_speaker__profile', 'projects',                  'institutions', 'links')
        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = self.get_object().videos.all()
        return super().list(request, *args, **kwargs)


class RoadshowViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Roadshow.objects.prefetch_related('institutions')
    serializer_class = RoadshowSerializer

    def list(self, request, *args, **kwargs):
        self.pagination_class = None
        self.serializer_class = RoadshowListSerializer
        return super().list(request, *args, **kwargs)


class SessionViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Session.objects.prefetch_related('session_type')
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = SessionSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related('main_speaker__profile')
        self.pagination_class = None
        self.serializer_class = SessionListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related('main_speaker__profile__institution', 'projects',
                                                       'private_files', 'links')
        return super().retrieve(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        # permission_classes=(HasRegistrationForEvent,),
        serializer_class=RegistrationListSerializer,
    )
    def attendees(self, request, *args, **kwargs):
        self.queryset = self.get_object().registrations \
                            .select_related('user__profile') \
                            .prefetch_related('user__profile__institution', 'user__profile__second_institution') \
                            .prefetch_related('user__profile__projects')

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
