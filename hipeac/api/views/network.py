from django.contrib.auth import get_user_model
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Institution, Project
from ..permissions import NetworkAdminPermission
from ..serializers import (
    InstitutionListSerializer, InstitutionSerializer,
    ProjectListSerializer, ProjectSerializer,
    UserPublicListSerializer, UserPublicSerializer
)


class InstitutionViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Institution.objects.all()
    permission_classes = (NetworkAdminPermission,)
    serializer_class = InstitutionSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer('description')
        self.serializer_class = InstitutionListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.select_related('parent').prefetch_related('children', 'links')
        return super().retrieve(request, *args, **kwargs)


class MemberViewSet(ListModelMixin, GenericViewSet):
    queryset = get_user_model().objects.filter(id__lte=100) \
                               .prefetch_related('profile__institution', 'profile__second_institution')
    pagination_class = None
    serializer_class = UserPublicSerializer

    def list(self, request, *args, **kwargs):
        self.serializer_class = UserPublicListSerializer
        return super().list(request, *args, **kwargs)


class ProjectViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Project.objects.all()
    pagination_class = None
    permission_classes = (NetworkAdminPermission,)
    serializer_class = ProjectSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer('description')
        self.serializer_class = ProjectListSerializer
        return super().list(request, *args, **kwargs)
