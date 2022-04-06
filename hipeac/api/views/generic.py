from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Metadata
from ..serializers import MetadataListSerializer


class MetadataViewSet(ListModelMixin, GenericViewSet):
    queryset = Metadata.objects.all()
    pagination_class = None
    serializer_class = MetadataListSerializer
