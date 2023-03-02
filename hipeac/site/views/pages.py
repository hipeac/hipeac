from hipeac.api.serializers import EventListSerializer
from hipeac.api.serializers.v2 import ArticleListSerializer, VideoListSerializer
from hipeac.models import Article, Event, Video

from .inertia import InertiaView


class HomeView(InertiaView):
    vue_entry_point = "apps/home/main.ts"

    def get_props(self, request, *args, **kwargs):
        articles = Article.objects.published().order_by("-publication_date")[:10]
        events = Event.objects.filter().order_by("-start_date")[:14]
        video = Video.objects.filter(shows_on_homepage=True).first()

        return {
            "articles": ArticleListSerializer(articles, many=True, context={"request": request}).data,
            "events": EventListSerializer(events, many=True, context={"request": request}).data,
            "video": VideoListSerializer(video, context={"request": request}).data if video else None,
        }


class JobsView(InertiaView):
    page_title = "Jobs"
    vue_entry_point = "apps/jobs/main.ts"
