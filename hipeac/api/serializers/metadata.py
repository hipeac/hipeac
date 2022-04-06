from rest_framework import serializers

from hipeac.models import Metadata


class MetadataSerializer(serializers.ModelSerializer):
    value = serializers.CharField(read_only=True)

    class Meta:
        model = Metadata
        fields = ("id", "value")


class MetadataWithEuraxessSerializer(MetadataSerializer):
    class Meta:
        model = Metadata
        fields = ("id", "value", "euraxess_value")


class MetadataListSerializer(MetadataSerializer):
    class Meta:
        model = Metadata
        fields = ("id", "type", "value")
