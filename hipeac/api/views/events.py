from django.db import IntegrityError
from django.views.decorators.cache import never_cache
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.parsers import FileUploadParser
from rest_framework.viewsets import GenericViewSet

from hipeac.models import B2b, Course, Event, File, Registration, Roadshow, Session, SessionAccessLink
from ..permissions import (
    B2bPermission,
    HasAdminPermissionOrReadOnly,
    HasManagementPermission,
    HasRegistrationForEvent,
    RegistrationPermission,
)
from ..serializers import (
    ArticleListSerializer,
    AuthRegistrationSerializer,
    B2bSerializer,
    CommitteeListSerializer,
    CourseListSerializer,
    EventListSerializer,
    EventManagementSerializer,
    EventSerializer,
    JobNestedSerializer,
    RegistrationListSerializer,
    RegistrationManagementSerializer,
    RoadshowListSerializer,
    RoadshowSerializer,
    SessionListSerializer,
    SessionSerializer,
    SessionAccessLinkSerializer,
    VideoListSerializer,
)


class B2bViewSet(UpdateModelMixin, GenericViewSet):
    queryset = B2b.objects.all()
    permission_classes = (B2bPermission,)
    serializer_class = B2bSerializer


class EventViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Event.objects.public()
    serializer_class = EventSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer("logistics")
        self.pagination_class = None
        self.serializer_class = EventListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.select_related("coordinating_institution").prefetch_related(
            "breaks",
            "fees",
            "links",
            "venues__rooms",
            "sponsors__institution",
            "sponsors__project",
            "sessions__session_type",
        )
        return super().retrieve(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=ArticleListSerializer,
    )
    def articles(self, request, *args, **kwargs):
        self.queryset = self.get_object().articles.prefetch_related("institutions", "projects")
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        permission_classes=(HasRegistrationForEvent,),
        serializer_class=RegistrationListSerializer,
    )
    def attendees(self, request, *args, **kwargs):
        self.queryset = (
            self.get_object()
            .registrations.select_related("user__profile")
            .prefetch_related("user__profile__institution", "user__profile__second_institution")
            .prefetch_related("user__profile__projects")
            .filter(status=Registration.STATUS_ACCEPTED)
        )

        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=B2bSerializer,
    )
    @never_cache
    def b2b(self, request, *args, **kwargs):
        self.queryset = self.get_object().b2b
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=CommitteeListSerializer,
    )
    def committees(self, request, *args, **kwargs):
        self.queryset = self.get_object().committees.prefetch_related("members__profile__institution")
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=CourseListSerializer,
    )
    def courses(self, request, *args, **kwargs):
        self.queryset = self.get_object().courses.prefetch_related(
            "teachers__profile__institution", "sessions", "private_files", "links"
        )
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
        self.queryset = (
            self.get_object()
            .registrations.select_related("user__profile")
            .prefetch_related("user__profile__institution", "user__profile__second_institution")
            .prefetch_related("user__profile__projects")
            .filter(status=Registration.STATUS_ACCEPTED)
        )

        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=SessionSerializer,
    )
    def sessions(self, request, *args, **kwargs):
        session_type = request.query_params.get("session_type", False)
        if not session_type:
            raise PermissionDenied("Please include a `session_type` query parameter in your request.")

        self.queryset = (
            self.get_object()
            .sessions.filter(session_type=session_type)
            .prefetch_related("session_type", "main_speaker__profile", "projects", "institutions", "links")
        )
        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = self.get_object().videos.all()
        return super().list(request, *args, **kwargs)


class EventManagementViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Event.objects.all()
    permission_classes = (HasManagementPermission,)
    serializer_class = EventManagementSerializer

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.select_related("coordinating_institution").prefetch_related(
            "breaks",
            "fees",
            "links",
            "venues__rooms",
            "sponsors__institution",
            "sponsors__project",
            "sessions__session_type",
        )
        return super().retrieve(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=RegistrationManagementSerializer,
    )
    def registrations(self, request, *args, **kwargs):
        self.queryset = (
            self.get_object()
            .registrations.select_related("user__profile")
            .prefetch_related("courses", "sessions", "posters", "files")
            .prefetch_related("user__profile__institution", "user__profile__second_institution")
            .prefetch_related("user__profile__projects")
            .prefetch_related("user__profile__links")
            .filter(status=Registration.STATUS_ACCEPTED)
        )

        return super().list(request, *args, **kwargs)


class RoadshowViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Roadshow.objects.prefetch_related("institutions")
    serializer_class = RoadshowSerializer

    def list(self, request, *args, **kwargs):
        self.pagination_class = None
        self.serializer_class = RoadshowListSerializer
        return super().list(request, *args, **kwargs)


class CourseViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Course.objects.all()
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = CourseListSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related("teachers__profile")
        self.pagination_class = None
        self.serializer_class = CourseListSerializer
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        # permission_classes=(HasRegistrationForEvent,),
        serializer_class=RegistrationListSerializer,
    )
    def attendees(self, request, *args, **kwargs):
        self.queryset = (
            self.get_object()
            .registrations.select_related("user__profile")
            .prefetch_related("user__profile__institution", "user__profile__second_institution")
            .prefetch_related("user__profile__projects")
            .filter(status=Registration.STATUS_ACCEPTED)
        )

        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = self.get_object().videos
        return super().list(request, *args, **kwargs)


class SessionViewSet(CourseViewSet):
    queryset = Session.objects.prefetch_related("session_type")
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = SessionSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related("main_speaker__profile")
        self.pagination_class = None
        self.serializer_class = SessionListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related(
            "main_speaker__profile__institution", "projects", "private_files", "links"
        )
        return super().retrieve(request, *args, **kwargs)


class RegistrationViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Registration.objects.prefetch_related("courses", "sessions", "posters")
    permission_classes = (RegistrationPermission,)
    serializer_class = AuthRegistrationSerializer

    def get_queryset_for_event(self):
        event_id = self.request.query_params.get("event_id", None)
        queryset = Registration.objects.filter(user_id=self.request.user.id).prefetch_related(
            "courses", "sessions", "posters"
        )
        if event_id is not None:
            queryset = queryset.filter(event_id=event_id)
        return queryset

    def perform_create(self, serializer):
        event = Event.objects.get(id=self.request.data["event"])
        if not event or not event.is_open_for_registration():
            raise ValidationError({"message": ["Registrations are closed for this event."]})

        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({"message": ["Duplicate entry - this user already has a registration."]})

    @never_cache
    def list(self, request, *args, **kwargs):
        self.queryset = self.get_queryset_for_event()
        return super().list(request, *args, **kwargs)

    @never_cache
    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.get_queryset_for_event()
        return super().retrieve(request, *args, **kwargs)

    @never_cache
    @action(detail=True, queryset=SessionAccessLink.objects.all())
    def access_links(self, request, *args, **kwargs):
        """
        Retrieve personalized Zoom links for the registered sessions.
        """
        registration = Registration.objects.get(id=kwargs.get("pk"))
        session_ids = list(Session.objects.filter(event_id=registration.event_id).values_list("id", flat=True))
        self.queryset = SessionAccessLink.objects.filter(user_id=self.request.user.id, session_id__in=session_ids)
        self.pagination_class = None
        self.serializer_class = SessionAccessLinkSerializer
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["POST"])
    def accept(self, request, *args, **kwargs):
        registration = self.get_object()

        if not registration.status == Registration.STATUS_ACCEPTED_INTERNALLY:
            raise ValidationError({"message": ["Registration status cannot be updated."]})

        registration.status = Registration.STATUS_ACCEPTED
        registration.save()
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["POST"])
    def reject(self, request, *args, **kwargs):
        registration = self.get_object()

        if not registration.status == Registration.STATUS_ACCEPTED_INTERNALLY:
            raise ValidationError({"message": ["Registration status cannot be updated."]})

        registration.status = Registration.STATUS_REJECTED
        registration.save()
        return super().retrieve(request, *args, **kwargs)

    """
    @action(
        detail=True, methods=["POST"], parser_classes=(FileUploadParser,),
    )
    def add_abstract(self, request, pk):
        abstract = AcacesPosterAbstract(file=request.data["file"])
        abstract.registration = self.get_object()
        abstract.save()
        return Response(status=201)
    """

    @action(
        detail=True,
        methods=["post"],
        pagination_class=None,
        serializer_class=AuthRegistrationSerializer,
        parser_classes=[FileUploadParser],
    )
    @never_cache
    def files(self, request, *args, **kwargs):
        registration = self.get_object()

        try:
            max_files = 1
            if registration.files.count() >= max_files:
                raise ValidationError({"files": [f"You have reached the limit on number of files ({max_files})."]})
        except KeyError:
            raise ValidationError({"files": ["Registration is not accepting files."]})

        File(content_object=registration, type=File.PUBLIC, file=request.data["file"]).save()

        return RetrieveModelMixin.retrieve(self, request, *args, **kwargs)
