from django.contrib.auth import get_user_model
from django.views.decorators.cache import never_cache
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Profile, Video
from ..serializers import (
    AuthUserSerializer, UserPublicSerializer, UserPublicListSerializer,
    PublicationListSerializer, VideoListSerializer
)


class UserViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = get_user_model().objects.filter(is_active=True) \
                                       .select_related('profile__institution') \
                                       .prefetch_related('profile__second_institution')
    serializer_class = UserPublicSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer('profile__bio')
        self.serializer_class = UserPublicListSerializer
        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=PublicationListSerializer)
    def publications(self, request, *args, **kwargs):
        self.queryset = Profile.objects.get(user_id=kwargs.get('pk')).publications.all()
        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = Video.objects.filter(user_id=kwargs.get('pk'))
        return super().list(request, *args, **kwargs)


class AuthUserViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = AuthUserSerializer

    def get_object(self):
        return self.request.user

    @action(methods=['get', 'patch', 'put'], detail=False, serializer_class=AuthUserSerializer)
    @never_cache
    def account(self, request, *args, **kwargs):
        return {
            'get': self.retrieve,
            'patch': self.partial_update,
            'put': self.update,
        }[request.method.lower()](request, *args, **kwargs)
