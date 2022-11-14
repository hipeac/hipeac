from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Publication, PublicationConference
from ...serializers import PublicationListSerializer, PublicationConferenceListSerializer


class PublicationConferenceViewSet(ListModelMixin, GenericViewSet):
    queryset = PublicationConference.objects.all()
    pagination_class = None
    serializer_class = PublicationConferenceListSerializer


class PaperAwardViewSet(ListModelMixin, GenericViewSet):
    pagination_class = None
    serializer_class = PublicationListSerializer

    def list(self, request, *args, **kwargs):
        year = request.query_params.get("year", False)
        if not year:
            raise PermissionDenied("Please include a `year` query parameter in your request.")

        self.queryset = Publication.objects.awarded(year=int(year))
        return super().list(request, *args, **kwargs)
