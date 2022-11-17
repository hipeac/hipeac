from rest_framework import serializers


class KeywordsMixin(serializers.ModelSerializer):
    keywords = serializers.JSONField(read_only=True)


from .files import FileSerializer
from .links import LinkSerializer
from .metadata import ApplicationAreaSerializer, MetadataSerializer, TopicSerializer


class ApplicationAreasMixin(serializers.ModelSerializer):
    application_areas = MetadataSerializer(many=True, read_only=True)
    rel_application_areas = ApplicationAreaSerializer(many=True)


class FilesMixin(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)


class LinksMixin(serializers.ModelSerializer):
    links = LinkSerializer(many=True)


class TopicsMixin(serializers.ModelSerializer):
    topics = MetadataSerializer(many=True, read_only=True)
    rel_topics = TopicSerializer(many=True)
