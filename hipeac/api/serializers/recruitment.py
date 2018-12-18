from django_countries.serializer_fields import CountryField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Job, JobEvaluation
from hipeac.models.recruitment import validate_institution
from hipeac.models.generic import HipeacCountries
from .generic import JsonField, LinkSerializer, MetadataField, MetadataListField
from .institutions import InstitutionNestedSerializer
from .projects import ProjectNestedSerializer


class JobBaseSerializer(WritableNestedModelSerializer):
    country = CountryField(country_dict=True, countries=HipeacCountries())
    application_areas = MetadataListField()
    topics = MetadataListField()
    career_levels = MetadataListField()
    employment_type = MetadataField()
    keywords = JsonField(read_only=True)
    email = serializers.EmailField(required=True)
    url = serializers.HyperlinkedIdentityField(view_name='v1:job-detail', read_only=True)
    href = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Job
        exclude = ('description', 'share', 'reminder_sent_for', 'evaluation_sent_for')


class JobNestedSerializer(JobBaseSerializer):
    institution = InstitutionNestedSerializer()
    project = ProjectNestedSerializer(required=False, allow_null=True)


class JobSerializer(JobBaseSerializer):
    links = LinkSerializer(required=False, many=True, allow_null=True)

    class Meta(JobBaseSerializer.Meta):
        exclude = ('share', 'reminder_sent_for', 'evaluation_sent_for', 'created_by')

    def validate_institution(self, data):
        validate_institution(data, self.context['request'].user)
        return data


class JobEvaluationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='v1:job-evaluation-detail', read_only=True)

    class Meta:
        model = JobEvaluation
        exclude = ()
