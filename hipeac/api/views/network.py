from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import HipeacPartner, Institution, Project, Video
from ..permissions import HasAdminPermissionOrReadOnly
from ..serializers import (
    HipeacPartnerListSerializer,
    InstitutionListSerializer,
    InstitutionMiniSerializer,
    InstitutionSerializer,
    ProjectMiniSerializer,
    ProjectListSerializer,
    ProjectSerializer,
    JobNestedSerializer,
    VideoListSerializer,
)


class InstitutionViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    filter_backends = (SearchFilter,)
    queryset = Institution.objects.all()
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = InstitutionSerializer
    search_fields = ("name", "local_name", "colloquial_name")

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer("description")
        self.serializer_class = InstitutionListSerializer
        return super().list(request, *args, **kwargs)

    @action(detail=False, pagination_class=None, serializer_class=InstitutionMiniSerializer)
    def all(self, request, *args, **kwargs):
        self.queryset = self.queryset.only("id", "name", "local_name", "colloquial_name", "type", "country", "image")
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.select_related("parent").prefetch_related("children", "links")
        return super().retrieve(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=JobNestedSerializer,
    )
    def jobs(self, request, *args, **kwargs):
        self.queryset = self.get_object().jobs.active()
        return super().list(request, *args, **kwargs)


class PartnerViewSet(ListModelMixin, GenericViewSet):
    queryset = HipeacPartner.objects.filter(
        hipeac__start_date__lte=timezone.now().date(), hipeac__end_date__gt=timezone.now().date()
    ).prefetch_related("institution", "representative__profile__institution")
    pagination_class = None
    serializer_class = HipeacPartnerListSerializer


class ProjectViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    filter_backends = (SearchFilter,)
    queryset = (
        Project.objects.select_related("programme")
        .prefetch_related(
            "rel_application_areas__application_area",
            "rel_institutions__institution",
            "rel_topics__topic",
        )
        .order_by("acronym")
    )
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = ProjectSerializer
    search_fields = ("acronym", "name")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer("description").filter(is_visible=True)
        self.serializer_class = ProjectListSerializer
        return super().list(request, *args, **kwargs)

    @action(detail=False, pagination_class=None, serializer_class=ProjectListSerializer)
    def all(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(is_visible=True)
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=JobNestedSerializer,
    )
    def jobs(self, request, *args, **kwargs):
        self.queryset = self.get_object().jobs.active()
        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = Video.objects.prefetch_related(
            "rel_application_areas__application_area", "rel_topics__topic"
        ).filter(rel_projects__project_id=kwargs.get("pk"))
        return super().list(request, *args, **kwargs)
