from django.contrib.auth import get_user_model
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from ..serializers import UserPublicListSerializer, UserPublicSerializer


class UserViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = get_user_model().objects.all()

    def list(self, request, *args, **kwargs):
        self.serializer_class = UserPublicListSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = UserPublicSerializer
        return super().retrieve(request, *args, **kwargs)
