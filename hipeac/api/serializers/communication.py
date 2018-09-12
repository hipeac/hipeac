from rest_framework import serializers

from hipeac.models import Article, Clipping, Quote, Video
from .institutions import InstitutionNestedSerializer


class ArticleListSerializer(serializers.ModelSerializer):
    href = serializers.CharField(source='get_absolute_url', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Article
        exclude = ('content',)


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


class VideoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
