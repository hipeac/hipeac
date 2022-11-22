from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Metadata, Project, RelatedProject
from .institutions import InstitutionNestedSerializer, InstitutionsMixin
from .mixins import ApplicationAreasMixin, LinksMixin, TopicsMixin


class ProjectSerializer(
    ApplicationAreasMixin, InstitutionsMixin, LinksMixin, TopicsMixin, WritableNestedModelSerializer
):
    self = serializers.HyperlinkedIdentityField(view_name="v1:project-detail", read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)  # deprecated
    href = serializers.CharField(source="get_absolute_url", read_only=True)
    programme = serializers.PrimaryKeyRelatedField(queryset=Metadata.objects.all())
    ec_project_id = serializers.CharField(allow_null=True, read_only=True)
    coordinating_institution = InstitutionNestedSerializer()

    class Meta:
        model = Project
        read_only_fields = ("image", "images")
        exclude = ()


class ProjectMiniSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = ("id", "self", "url", "href", "acronym", "name")


class ProjectNestedSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = ("id", "self", "url", "href", "acronym", "name", "programme", "start_date", "end_date", "images")


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


class RelatedProjectSerializer(serializers.ModelSerializer):
    oid = serializers.PrimaryKeyRelatedField(source="project", queryset=Project.objects.all())

    class Meta:
        model = RelatedProject
        fields = ("id", "oid")


class ProjectsMixin(serializers.ModelSerializer):
    projects = ProjectNestedSerializer(many=True, read_only=True)
    rel_projects = RelatedProjectSerializer(many=True)
