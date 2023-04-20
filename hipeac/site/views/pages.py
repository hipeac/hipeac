from django.views import generic

from hipeac.api.serializers.communication import VideoListSerializer
from hipeac.models.communication.videos import Video
from .inertia import render_inertia


class HomeView(generic.View):
    def get(self, request, *args, **kwargs):
        video = Video.objects.filter(shows_on_homepage=True).first()

        return render_inertia(
            request,
            "apps/home/main.ts",
            props={
                "video": VideoListSerializer(video, context={"request": request}).data if video else None,
            },
        )
