from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Article, Clipping, Quote, Video
from ..serializers import ArticleListSerializer, ClippingListSerializer, QuoteListSerializer, VideoListSerializer


class ArticleViewSet(ListModelMixin, GenericViewSet):
    queryset = Article.objects.prefetch_related('event', 'institutions', 'projects')
    pagination_class = None
    serializer_class = ArticleListSerializer


class ClippingViewSet(ListModelMixin, GenericViewSet):
    queryset = Clipping.objects.all()
    pagination_class = None
    serializer_class = ClippingListSerializer


class QuoteViewSet(ListModelMixin, GenericViewSet):
    queryset = Quote.objects.prefetch_related('institution')
    pagination_class = None
    serializer_class = QuoteListSerializer


class VideoViewSet(ListModelMixin, GenericViewSet):
    queryset = Video.objects.prefetch_related('institution')
    pagination_class = None
    serializer_class = VideoListSerializer
