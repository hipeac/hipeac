from rest_framework import serializers
from rest_framework.relations import RelatedField

from hipeac.models import Project
from .generic import MetadataListField
from .institutions import InstitutionRelatedField


class ProjectNestedSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='v1:project-detail', read_only=True)
    href = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Project
        read_only_fields = ['image', 'images']
        fields = ['id', 'acronym', 'name', 'images', 'url', 'href']


class ProjectListSerializer(ProjectNestedSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()

    class Meta(ProjectNestedSerializer.Meta):
        fields = ProjectNestedSerializer.Meta.fields + ['application_areas', 'topics']


class ProjectSerializer(ProjectNestedSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()
    coordinating_institution = InstitutionRelatedField()
    partners = InstitutionRelatedField(many=True, required=False)
    slug = serializers.CharField(read_only=True)

    open_positions = serializers.SerializerMethodField()

    class Meta(ProjectNestedSerializer.Meta):
        fields = None
        exclude = ()

    def get_open_positions(self, obj):
        from .recruitment import JobNestedSerializer  # noqa
        jobs = obj.jobs.active().defer('description')
        return JobNestedSerializer(jobs, many=True, context=self.context).data


class ProjectRelatedField(RelatedField):
    queryset = Project.objects.all()

    def to_internal_value(self, data):
        return self.get_queryset().get(id=data['id'])

    def to_representation(self, obj):
        return ProjectNestedSerializer(obj, context=self.context).data
