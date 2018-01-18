from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Metadata
from ..serializers import MetadataListSerializer


class MetadataViewSet(ListModelMixin, GenericViewSet):
    queryset = Metadata.objects.all()
    pagination_class = None

    def list(self, request, *args, **kwargs):
        self.serializer_class = MetadataListSerializer
        return super().list(request, *args, **kwargs)
