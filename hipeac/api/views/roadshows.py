from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Dissemination

from ..serializers.v2 import RoadshowSerializer


class RoadshowViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Dissemination.objects.filter(type="roadshow")
    serializer_class = RoadshowSerializer

    def list(self, request, *args, **kwargs):
        self.pagination_class = None
        self.serializer_class = RoadshowSerializer
        return super().list(request, *args, **kwargs)
