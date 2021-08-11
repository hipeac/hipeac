from rest_framework.mixins import DestroyModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import File
from ..permissions import FilePermission
from ..serializers import FileSerializer


class FileViewSet(DestroyModelMixin, GenericViewSet):
    permission_classes = (FilePermission,)
    queryset = File.objects.all()
    serializer_class = FileSerializer
