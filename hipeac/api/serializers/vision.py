from hipeac.models.communication import article
from rest_framework import serializers

from hipeac.models import Link, Vision, VisionArticle
from .generic import ImageSerializer, PublicFileSerializer


class VisionArticleSerializer(serializers.ModelSerializer):
    download_url = serializers.CharField(source="get_download_url", read_only=True)

    class Meta:
        model = VisionArticle
        exclude = ("vision", "position", "file")


class VisionSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    public_files = PublicFileSerializer(many=True, read_only=True)
    download_url = serializers.CharField(source="get_download_url", read_only=True)
    youtube_url = serializers.SerializerMethodField(read_only=True)
    articles = VisionArticleSerializer(many=True)

    class Meta:
        model = Vision
        exclude = ("file_draft", "file", "downloads")

    def get_youtube_url(self, obj) -> str:
        return obj.get_link(Link.YOUTUBE)


class VisionListSerializer(VisionSerializer):
    pass
