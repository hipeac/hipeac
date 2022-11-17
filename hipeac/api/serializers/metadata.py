from rest_framework import serializers

from hipeac.models import ApplicationArea, Metadata, Topic
from .mixins import KeywordsMixin


class MetadataSerializer(KeywordsMixin, serializers.ModelSerializer):
    value = serializers.CharField(read_only=True)

    class Meta:
        model = Metadata
        exclude = ("euraxess_value",)


class MetadataWithEuraxessSerializer(MetadataSerializer):
    class Meta:
        model = Metadata
        exclude = ()


class MetadataListSerializer(MetadataSerializer):
    class Meta:
        model = Metadata
        exclude = ("euraxess_value",)


class ApplicationAreaSerializer(serializers.ModelSerializer):
    mid = serializers.PrimaryKeyRelatedField(source="application_area", queryset=Metadata.objects.all())

    class Meta:
        model = ApplicationArea
        fields = ("id", "mid")


class TopicSerializer(serializers.ModelSerializer):
    mid = serializers.PrimaryKeyRelatedField(source="topic", queryset=Metadata.objects.all())

    class Meta:
        model = Topic
        fields = ("id", "mid")
