from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Clipping, Quote
from ..serializers import ClippingListSerializer, QuoteListSerializer


class ClippingViewSet(ListModelMixin, GenericViewSet):
    queryset = Clipping.objects.all()
    pagination_class = None
    serializer_class = ClippingListSerializer


class QuoteViewSet(ListModelMixin, GenericViewSet):
    queryset = Quote.objects.prefetch_related('institution')
    pagination_class = None
    serializer_class = QuoteListSerializer
