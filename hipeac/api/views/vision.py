from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Dissemination, Vision
from ..serializers import DisseminationListSerializer, VisionListSerializer


class VisionViewSet(ListModelMixin, GenericViewSet):
    queryset = Vision.objects.published().prefetch_related("images", "links")
    pagination_class = None
    serializer_class = VisionListSerializer

    @action(detail=False, serializer_class=DisseminationListSerializer)
    def dissemination(self, request, *args, **kwargs):
        self.queryset = Dissemination.objects.filter(type="vision")
        return super().list(request, *args, **kwargs)
