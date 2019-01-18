from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Vision
from ..serializers import VisionListSerializer


class VisionViewSet(ListModelMixin, GenericViewSet):
    queryset = Vision.objects.published().prefetch_related('images', 'links')
    pagination_class = None
    serializer_class = VisionListSerializer
