from rest_framework import serializers

from hipeac.models import Link, Vision


class VisionListSerializer(serializers.ModelSerializer):
    youtube_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Vision
        fields = '__all__'

    def get_youtube_url(self, obj) -> str:
        return obj.get_link(Link.YOUTUBE)
