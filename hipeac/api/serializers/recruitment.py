from django_countries import Countries
from django_countries.serializer_fields import CountryField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.functions import get_european_countries, get_h2020_associated_countries
from hipeac.models import Job, JobEvaluation
from .institutions import InstitutionNestedSerializer
from .projects import ProjectNestedSerializer
from .mixins import ApplicationAreasMixin, KeywordsMixin, LinksMixin, TopicsMixin


class HipeacCountries(Countries):
    only = get_european_countries() + get_h2020_associated_countries()


class JobBaseSerializer(ApplicationAreasMixin, KeywordsMixin, TopicsMixin, WritableNestedModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:job-detail", read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)  # deprecated
    href = serializers.CharField(source="get_absolute_url", read_only=True)
    country = CountryField(country_dict=True, countries=HipeacCountries())
    email = serializers.EmailField(required=False, allow_blank=True)
    add_to_euraxess = serializers.BooleanField(required=True)
    institution = InstitutionNestedSerializer(required=True)
    project = ProjectNestedSerializer(required=False, allow_null=True)

    class Meta:
        model = Job
        exclude = ("description", "share", "reminder_sent_for", "evaluation_sent_for")


class JobNestedSerializer(JobBaseSerializer):
    pass


class JobSerializer(LinksMixin, JobBaseSerializer):
    class Meta(JobBaseSerializer.Meta):
        exclude = ("share", "reminder_sent_for", "evaluation_sent_for", "created_by")


class JobEvaluationSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:job-evaluation-detail", read_only=True)
    job = JobSerializer(read_only=True)

    class Meta:
        model = JobEvaluation
        exclude = ()
