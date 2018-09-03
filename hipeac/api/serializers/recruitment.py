from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from hipeac.functions import HipeacCountries
from hipeac.models import Job
from .generic import JsonField, MetadataField, MetadataListField
from .institutions import InstitutionRelatedField
from .projects import ProjectRelatedField


class JobNestedSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True, countries=HipeacCountries())
    institution = InstitutionRelatedField()
    project = ProjectRelatedField(required=False, allow_null=True)
    application_areas = MetadataListField()
    topics = MetadataListField()
    career_levels = MetadataListField()
    employment_type = MetadataField()
    keywords = JsonField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='v1:job-detail', read_only=True)
    href = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Job
        exclude = ['description', 'share', 'last_reminder', 'created_at']


class JobSerializer(JobNestedSerializer):
    class Meta(JobNestedSerializer.Meta):
        exclude = ['share', 'last_reminder', 'created_at', 'created_by']
