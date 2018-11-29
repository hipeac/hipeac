from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Project
from .generic import LinkSerializer, MetadataListField


class ProjectAllSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ('id', 'acronym', 'name', 'ec_project_id')


class ProjectNestedSerializer(WritableNestedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='v1:project-detail', read_only=True)
    href = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Project
        read_only_fields = ('image', 'images')
        fields = ['id', 'acronym', 'name', 'programme', 'start_date', 'end_date', 'images', 'url', 'href']


class ProjectListSerializer(ProjectNestedSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()

    class Meta(ProjectNestedSerializer.Meta):
        fields = ProjectNestedSerializer.Meta.fields + ['application_areas', 'topics']


class ProjectSerializer(ProjectNestedSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()
    slug = serializers.CharField(read_only=True)
    links = LinkSerializer(many=True)

    open_positions = serializers.SerializerMethodField(read_only=True)

    class Meta(ProjectNestedSerializer.Meta):
        fields = None
        exclude = ()

    def get_open_positions(self, obj):
        from .recruitment import JobNestedSerializer  # noqa
        jobs = obj.jobs.active().defer('description')
        return JobNestedSerializer(jobs, many=True, context=self.context).data
