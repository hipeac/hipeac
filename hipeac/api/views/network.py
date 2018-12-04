from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Institution, Project, Video
from ..permissions import HasAdminPermissionOrReadOnly
from ..serializers import (
    InstitutionAllSerializer, InstitutionListSerializer, InstitutionSerializer,
    ProjectAllSerializer, ProjectListSerializer, ProjectSerializer,
    MemberPublicSerializer,
    VideoListSerializer
)


class InstitutionViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Institution.objects.all()
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = InstitutionSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer('description')
        self.serializer_class = InstitutionListSerializer
        return super().list(request, *args, **kwargs)

    @action(detail=False, pagination_class=None, serializer_class=InstitutionAllSerializer)
    def all(self, request, *args, **kwargs):
        self.queryset = self.queryset.only('id', 'name', 'local_name', 'colloquial_name', 'type', 'country')
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.select_related('parent').prefetch_related('children', 'links')
        return super().retrieve(request, *args, **kwargs)


class MemberViewSet(ListModelMixin, GenericViewSet):
    queryset = get_user_model().objects.filter(is_active=True) \
                                       .select_related('profile__institution') \
                                       .order_by('first_name', 'last_name') \
                                       .defer('profile__bio', 'affiliates__bio')

    pagination_class = None
    serializer_class = MemberPublicSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(
            is_active=True,
            profile__membership_tags__contains='member', profile__membership_revocation_date__isnull=True
        )
        return super().list(request, *args, **kwargs)

    @action(detail=False)
    def affiliates(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(
            is_active=True,
            profile__membership_tags__contains='affiliated', profile__membership_revocation_date__isnull=True
        )
        return super().list(request, *args, **kwargs)


class ProjectViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Project.objects.all()
    pagination_class = None
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = ProjectSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer('description')
        self.serializer_class = ProjectListSerializer
        return super().list(request, *args, **kwargs)

    @action(detail=False, serializer_class=ProjectAllSerializer)
    def all(self, request, *args, **kwargs):
        self.queryset = self.queryset.only('id', 'programme', 'acronym', 'name', 'ec_project_id')
        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = Video.objects.filter(project_id=kwargs.get('pk'))
        return super().list(request, *args, **kwargs)
