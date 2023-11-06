from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Article, Clipping, Magazine, Quote, Video

from ..serializers import (
    ArticleListSerializer,
    ClippingListSerializer,
    MagazineListSerializer,
    QuoteListSerializer,
    VideoListSerializer,
)


class ArticleViewSet(ListModelMixin, GenericViewSet):
    queryset = Article.objects.published()
    pagination_class = None
    serializer_class = ArticleListSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer("excerpt", "content")
        return super().list(request, *args, **kwargs)


class ClippingViewSet(ListModelMixin, GenericViewSet):
    queryset = Clipping.objects.all()
    pagination_class = None
    serializer_class = ClippingListSerializer


class QuoteViewSet(ListModelMixin, GenericViewSet):
    queryset = Quote.objects.all()
    pagination_class = None
    serializer_class = QuoteListSerializer


class MagazineViewSet(ListModelMixin, GenericViewSet):
    queryset = Magazine.objects.all().prefetch_related("images")
    pagination_class = None
    serializer_class = MagazineListSerializer


class VideoViewSet(ListModelMixin, GenericViewSet):
    queryset = Video.objects.filter(is_expert=True).prefetch_related(
        "users__profile__institution", "users__profile__second_institution"
    )
    pagination_class = None
    serializer_class = VideoListSerializer
