from django.views.decorators.cache import never_cache
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Publication, PublicationConference, TechTransferCall, TechTransferApplication
from ..serializers import (
    PublicationListSerializer, PublicationConferenceListSerializer,
    TechTransferCallSerializer, TechTransferApplicationSerializer
)


class PublicationConferenceViewSet(ListModelMixin, GenericViewSet):
    queryset = PublicationConference.objects.all()
    pagination_class = None
    serializer_class = PublicationConferenceListSerializer


class PaperAwardViewSet(ListModelMixin, GenericViewSet):
    pagination_class = None
    serializer_class = PublicationListSerializer

    def list(self, request, *args, **kwargs):
        year = request.query_params.get('year', False)
        if not year:
            raise PermissionDenied('Please include a `year` query parameter in your request.')

        self.queryset = Publication.objects.awarded(year=int(year))
        return super().list(request, *args, **kwargs)


class TechTransferViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    pagination_class = None
    serializer_class = TechTransferApplicationSerializer

    def get_object(self):
        return TechTransferCall.objects.active()

    @action(detail=False, serializer_class=TechTransferCallSerializer)
    @never_cache
    def call(self, request, *args, **kwargs):
        return RetrieveModelMixin.retrieve(self, request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.queryset = TechTransferApplication.objects.filter(awarded=True).prefetch_related('call')
        return super().list(request, *args, **kwargs)
