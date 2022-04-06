from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.api.serializers.events.acaces import AcacesSerializer
from hipeac.models import Acaces, AcacesCourse, AcacesGrant, AcacesRegistration
from ...permissions import AcacesManagementPermission, HasAdminPermissionOrReadOnly, HasRegistrationForRelatedEvent
from ...serializers import (
    AcacesCourseSerializer,
    AcacesGrantSerializer,
    AcacesRegistrationManagementSerializer,
    CourseListSerializer,
    RegistrationListSerializer,
    VideoListSerializer,
)


class AcacesViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Acaces.objects.all()
    registration_model = AcacesRegistration
    serializer_class = AcacesSerializer

    @action(detail=True, pagination_class=None, serializer_class=AcacesCourseSerializer)
    def courses(self, request, *args, **kwargs):
        self.queryset = AcacesCourse.objects.filter(event_id=kwargs.get("pk")).prefetch_related(
            "rel_users__user__profile__institution", "sessions", "files", "links"
        )
        return ListModelMixin.list(self, request, *args, **kwargs)


class AcacesCourseViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = AcacesCourse.objects.all()
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
        permission_classes=(HasRegistrationForRelatedEvent,),
        serializer_class=RegistrationListSerializer,
    )
    def attendees(self, request, *args, **kwargs):
        self.queryset = (
            self.get_object()
            .registrations.select_related("user__profile")
            .prefetch_related("user__profile__institution")
            .filter(acacesregistration__status=AcacesRegistration.STATUS_ADMITTED, acacesregistration__accepted=True)
        )

        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = self.get_object().videos
        return super().list(request, *args, **kwargs)


class AcacesManagementViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Acaces.objects.prefetch_related(
        "links",
        "sessions__type",
        "sessions__rel_application_areas__application_area",
        "sessions__rel_topics__topic",
        "sessions__main_speaker__profile__institution",
    )
    permission_classes = (AcacesManagementPermission,)
    serializer_class = AcacesSerializer

    @method_decorator(never_cache)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(never_cache)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=AcacesCourseSerializer)
    @method_decorator(never_cache)
    def courses(self, request, *args, **kwargs):
        self.queryset = AcacesCourse.objects.filter(event_id=kwargs.get("pk")).prefetch_related(
            "rel_users__user__profile__institution", "sessions", "files", "links"
        )
        return ListModelMixin.list(self, request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=AcacesRegistrationManagementSerializer)
    @method_decorator(never_cache)
    def registrations(self, request, *args, **kwargs):
        self.queryset = (
            AcacesRegistration.objects.filter(event_id=kwargs.get("pk"))
            .prefetch_related(
                "user__profile__gender",
                "user__profile__meal_preference",
                "user__profile__institution",
                "courses",
                "sessions",
            )
            .select_related("poster")
        )
        return ListModelMixin.list(self, request, *args, **kwargs)


class AcacesGrantManagementViewSet(UpdateModelMixin, GenericViewSet):
    queryset = AcacesGrant.objects.all()
    permission_classes = (AcacesManagementPermission,)
    serializer_class = AcacesGrantSerializer


class AcacesRegistrationManagementViewSet(UpdateModelMixin, GenericViewSet):
    queryset = AcacesRegistration.objects.all()
    permission_classes = (AcacesManagementPermission,)
    serializer_class = AcacesRegistrationManagementSerializer
