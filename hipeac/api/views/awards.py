from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import TechTransferCall, TechTransferApplication
from ..serializers import TechTransferCallSerializer, TechTransferApplicationSerializer


class TechTransferViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    pagination_class = None
    serializer_class = TechTransferApplicationSerializer

    def get_object(self):
        return TechTransferCall.objects.active()

    @action(detail=False, serializer_class=TechTransferCallSerializer)
    @method_decorator(never_cache)
    def call(self, request, *args, **kwargs):
        return RetrieveModelMixin.retrieve(self, request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.queryset = TechTransferApplication.objects.filter(award__isnull=False).prefetch_related("call")
        return super().list(request, *args, **kwargs)
