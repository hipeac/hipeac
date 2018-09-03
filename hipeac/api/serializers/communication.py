from rest_framework import serializers

from hipeac.models import Clipping, Quote, Video
from .institutions import InstitutionNestedSerializer


class ClippingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clipping
        fields = '__all__'


class QuoteNestedSerializer(serializers.ModelSerializer):
    institution = InstitutionNestedSerializer()

    class Meta:
        model = Quote
        exclude = ['user']


class QuoteListSerializer(QuoteNestedSerializer):
    pass


class VideoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
