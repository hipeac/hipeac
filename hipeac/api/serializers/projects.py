from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Project
from .generic import LinkSerializer, MetadataField, MetadataListField


class ProjectSerializer(WritableNestedModelSerializer):
    programme = MetadataField(allow_null=True)
    application_areas = MetadataListField()
    topics = MetadataListField()
    links = LinkSerializer(many=True)
    url = serializers.HyperlinkedIdentityField(view_name='v1:project-detail', read_only=True)
    href = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Project
        read_only_fields = ('image', 'images')
        exclude = ()


class ProjectMiniSerializer(ProjectSerializer):

    class Meta:
        model = Project
        fields = ('id', 'acronym', 'name', 'ec_project_id')


class ProjectNestedSerializer(ProjectSerializer):

    class Meta:
        model = Project
        fields = ('id', 'acronym', 'name', 'programme', 'start_date', 'end_date', 'url', 'href', 'images')


class ProjectListSerializer(ProjectSerializer):

    class Meta:
        model = Project
        fields = ('id', 'acronym', 'name', 'programme', 'start_date', 'end_date', 'url', 'href', 'images',
                  'application_areas', 'topics')
