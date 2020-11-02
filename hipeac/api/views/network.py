from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from hipeac.models import HipeacPartner, Institution, Project
from ..permissions import HasAdminPermissionOrReadOnly
from ..serializers import (
    HipeacPartnerListSerializer,
    InstitutionNestedSerializer,
    InstitutionListSerializer,
    InstitutionMiniSerializer,
    InstitutionSerializer,
    ProjectMiniSerializer,
    ProjectListSerializer,
    ProjectSerializer,
    JobNestedSerializer,
    UserPublicMembershipSerializer,
    VideoListSerializer,
)


class InstitutionViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Institution.objects.all()
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = InstitutionSerializer

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
        detail=True, pagination_class=None, serializer_class=JobNestedSerializer,
    )
    def jobs(self, request, *args, **kwargs):
        self.queryset = self.get_object().jobs.active()
        return super().list(request, *args, **kwargs)


class MemberViewSet(ListModelMixin, GenericViewSet):
    queryset = (
        get_user_model()
        .objects.filter(is_active=True)
        .select_related("profile")
        .defer("profile__bio")
        .order_by("first_name", "last_name")
    )
    pagination_class = None
    serializer_class = UserPublicMembershipSerializer

    def list(self, request, *args, **kwargs):
        members = self.queryset.filter(
            profile__membership_tags__contains="member", profile__membership_revocation_date__isnull=True
        )
        affiliates = self.queryset.filter(
            profile__membership_tags__contains="affiliated", profile__membership_revocation_date__isnull=True
        )
        institution_ids = list(members.values_list("profile__institution_id", flat=True))
        second_institution_ids = list(members.values_list("profile__second_institution_id", flat=True))
        institutions = Institution.objects.filter(id__in=institution_ids + second_institution_ids)
        ctx = {"request": request}

        return Response(
            {
                "institutions": InstitutionNestedSerializer(institutions, many=True, context=ctx).data,
                "members": UserPublicMembershipSerializer(members, many=True, context=ctx).data,
                "affiliates": UserPublicMembershipSerializer(affiliates, many=True, context=ctx).data,
            }
        )

    @action(detail=False)
    def affiliates(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(
            is_active=True,
            profile__membership_tags__contains="affiliated",
            profile__membership_revocation_date__isnull=True,
        )
        return super().list(request, *args, **kwargs)


class PartnerViewSet(ListModelMixin, GenericViewSet):
    queryset = HipeacPartner.objects.filter(hipeac__visible=True).prefetch_related(
        "institution", "representative__profile"
    )
    pagination_class = None
    serializer_class = HipeacPartnerListSerializer


class ProjectViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Project.objects.order_by("acronym")
    pagination_class = None
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = ProjectSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer("description")
        self.serializer_class = ProjectListSerializer
        return super().list(request, *args, **kwargs)

    @action(detail=False, serializer_class=ProjectMiniSerializer)
    def all(self, request, *args, **kwargs):
        self.queryset = self.queryset.only("id", "programme", "acronym", "name", "ec_project_id", "image")
        return super().list(request, *args, **kwargs)

    @action(
        detail=True, pagination_class=None, serializer_class=JobNestedSerializer,
    )
    def jobs(self, request, *args, **kwargs):
        self.queryset = self.get_object().jobs.active()
        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = self.get_object().videos.all()
        return super().list(request, *args, **kwargs)
