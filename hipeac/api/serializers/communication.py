from rest_framework import serializers

from hipeac.models import Article, Clipping, Quote, Magazine, Video
from .generic import ImageSerializer, MetadataListField
from .institutions import InstitutionNestedSerializer
from .users import UserPublicListSerializer


class ArticleListSerializer(serializers.ModelSerializer):
    href = serializers.CharField(source='get_absolute_url', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Article
        exclude = ('created_by', 'excerpt', 'content', 'projects', 'institutions')


class ClippingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clipping
        fields = '__all__'


class QuoteNestedSerializer(serializers.ModelSerializer):
    institution = InstitutionNestedSerializer()

    class Meta:
        model = Quote
        exclude = ('user',)


class QuoteListSerializer(QuoteNestedSerializer):
    pass


class MagazineListSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    download_url = serializers.CharField(source='get_download_url', read_only=True)

    class Meta:
        model = Magazine
        exclude = ('file', 'file_tablet', 'downloads')


class VideoListSerializer(serializers.ModelSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()
    users = UserPublicListSerializer(many=True)

    class Meta:
        model = Video
        fields = '__all__'
