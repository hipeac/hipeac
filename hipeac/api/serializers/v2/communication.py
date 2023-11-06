from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from hipeac.models.communication import Article, Dissemination, Video

from ..mixins import ApplicationAreasMixin, TopicsMixin


class ArticleListSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Article
        exclude = ("is_ready", "created_at", "created_by", "excerpt", "content", "event")


class DisseminationSerializer(ApplicationAreasMixin, TopicsMixin, serializers.ModelSerializer):
    class Meta:
        model = Dissemination
        fields = "__all__"


class RoadshowSerializer(DisseminationSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    country = CountryField(country_dict=True)

    class Meta:
        model = Dissemination
        fields = ("id", "start_date", "end_date", "name", "country", "description", "url")


class VideoListSerializer(ApplicationAreasMixin, TopicsMixin, serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"
