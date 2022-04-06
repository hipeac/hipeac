from rest_framework import serializers

from .files import FileSerializer
from .links import LinkSerializer
from .metadata import MetadataSerializer


class ApplicationAreasMixin(serializers.ModelSerializer):
    application_areas = MetadataSerializer(many=True, read_only=True)


class FilesMixin(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)


class LinksMixin(serializers.ModelSerializer):
    links = LinkSerializer(many=True)


class TopicsMixin(serializers.ModelSerializer):
    topics = MetadataSerializer(many=True, read_only=True)
