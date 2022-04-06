from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Project
from .metadata import MetadataSerializer
from .mixins import ApplicationAreasMixin, LinksMixin, TopicsMixin


class ProjectSerializer(ApplicationAreasMixin, LinksMixin, TopicsMixin, WritableNestedModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:project-detail", read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    programme = MetadataSerializer(allow_null=True)
    ec_project_id = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        read_only_fields = ("image", "images")
        exclude = ()


class ProjectMiniSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = ("id", "self", "url", "acronym", "name")


class ProjectNestedSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = ("id", "self", "url", "acronym", "name", "programme", "start_date", "end_date", "images")


class ProjectListSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "self",
            "url",
            "acronym",
            "name",
            "programme",
            "start_date",
            "end_date",
            "images",
            "application_areas",
            "topics",
        )
