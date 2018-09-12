from django.contrib.auth import get_user_model
from django.views.decorators.cache import never_cache
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from ..serializers import AuthUserSerializer, UserPublicListSerializer, UserPublicSerializer


class UserViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = get_user_model().objects.all()

    def list(self, request, *args, **kwargs):
        self.serializer_class = UserPublicListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = UserPublicSerializer
        return super().retrieve(request, *args, **kwargs)


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
