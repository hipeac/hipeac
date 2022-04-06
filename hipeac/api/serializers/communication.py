from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from hipeac.models import Article, Clipping, Dissemination, Quote, Magazine, Video
from .generic import ImageSerializer
from .institutions import InstitutionNestedSerializer
from .metadata import MetadataSerializer
from .mixins import ApplicationAreasMixin, TopicsMixin
from .users import UserPublicMiniSerializer


class ArticleListSerializer(serializers.ModelSerializer):
    href = serializers.CharField(source="get_absolute_url", read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Article
        exclude = ("created_by", "excerpt", "content")


class ClippingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clipping
        fields = "__all__"


class DisseminationListSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)

    class Meta:
        model = Dissemination
        fields = "__all__"


class QuoteNestedSerializer(serializers.ModelSerializer):
    institutions = InstitutionNestedSerializer(many=True)

    class Meta:
        model = Quote
        exclude = ()


class QuoteListSerializer(QuoteNestedSerializer):
    pass


class MagazineListSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    download_url = serializers.CharField(source="get_download_url", read_only=True)

    class Meta:
        model = Magazine
        exclude = ("file", "downloads")


class VideoListSerializer(ApplicationAreasMixin, TopicsMixin, serializers.ModelSerializer):
    users = UserPublicMiniSerializer(many=True)

    class Meta:
        model = Video
        fields = "__all__"
