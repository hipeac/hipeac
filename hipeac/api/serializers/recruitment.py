from django_countries import Countries
from django_countries.serializer_fields import CountryField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.functions import get_european_countries, get_h2020_associated_countries
from hipeac.models import Job, JobEvaluation
from hipeac.models.recruitment import validate_institution
from .institutions import InstitutionNestedSerializer
from .projects import ProjectNestedSerializer
from .metadata import MetadataSerializer
from .mixins import ApplicationAreasMixin, LinksMixin, TopicsMixin


class HipeacCountries(Countries):
    only = get_european_countries() + get_h2020_associated_countries()


class JobBaseSerializer(ApplicationAreasMixin, TopicsMixin, WritableNestedModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:job-detail", read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)  # deprecated
    href = serializers.CharField(source="get_absolute_url", read_only=True)  # deprecated
    country = CountryField(country_dict=True, countries=HipeacCountries())
    career_levels = MetadataSerializer(many=True)
    employment_type = MetadataSerializer()
    keywords = serializers.JSONField(read_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    add_to_euraxess = serializers.BooleanField(required=True)

    class Meta:
        model = Job
        exclude = ("description", "share", "reminder_sent_for", "evaluation_sent_for")


class JobNestedSerializer(JobBaseSerializer):
    institution = InstitutionNestedSerializer()
    project = ProjectNestedSerializer(required=False, allow_null=True)


class JobSerializer(LinksMixin, JobBaseSerializer):
    class Meta(JobBaseSerializer.Meta):
        exclude = ("share", "reminder_sent_for", "evaluation_sent_for", "created_by")

    def validate_institution(self, data):
        validate_institution(data, self.context["request"].user)
        return data


class JobEvaluationSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:job-evaluation-detail", read_only=True)
    job = JobSerializer(read_only=True)

    class Meta:
        model = JobEvaluation
        exclude = ()
