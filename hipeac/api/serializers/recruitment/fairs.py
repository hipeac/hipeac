from django_countries.serializer_fields import CountryField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models.users import Profile
from hipeac.models.recruitment import Job, JobFair, JobFairRegistration
from ..files import FileSerializer
from ..institutions import InstitutionsMixin, InstitutionMiniSerializer
from ..metadata import MetadataSerializer
from ..mixins import ApplicationAreasMixin, LinksMixin, TopicsMixin
from ..users import UserPublicSerializer, UserPublicMiniSerializer


class JobFairSerializer(InstitutionsMixin, LinksMixin, WritableNestedModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:jobfair-detail", read_only=True)
    href = serializers.CharField(source="get_absolute_url", read_only=True)
    country = CountryField(country_dict=True)

    class Meta:
        model = JobFair
        exclude = ()


class JobFairRegistrationSerializer(WritableNestedModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:auth-registration-jobfair-detail", read_only=True)
    jobs = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all(), many=True, allow_empty=True)
    user = UserPublicMiniSerializer(read_only=True)

    class Meta:
        model = JobFairRegistration
        exclude = ()


class JobApplicantProfileMiniSerializer(ApplicationAreasMixin, TopicsMixin, serializers.ModelSerializer):
    country = CountryField(country_dict=True)
    name = serializers.CharField(read_only=True)
    institution = InstitutionMiniSerializer(read_only=True)
    cv = FileSerializer(read_only=True)
    gender = MetadataSerializer(allow_null=True)

    class Meta:
        model = Profile
        fields = ("name", "country", "institution", "bio", "cv", "gender", "application_areas", "topics")


class JobApplicantSerializer(UserPublicSerializer):
    profile = JobApplicantProfileMiniSerializer(read_only=True)

    class Meta(UserPublicSerializer.Meta):
        fields = UserPublicSerializer.Meta.fields + ("email",)


class JobApplicantRegistrationSerializer(serializers.ModelSerializer):
    user = JobApplicantSerializer(read_only=True)

    class Meta:
        model = JobFairRegistration
        fields = ("jobs", "user")
