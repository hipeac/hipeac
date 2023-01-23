from rest_framework import serializers

from hipeac.models import Article, Video
from ..mixins import ApplicationAreasMixin, TopicsMixin


class ArticleListSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Article
        exclude = ("is_ready", "created_at", "created_by", "excerpt", "content", "event")


class VideoListSerializer(ApplicationAreasMixin, TopicsMixin, serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = "__all__"
