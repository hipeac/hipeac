from django_countries.serializer_fields import CountryField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models.recruitment import Job, JobFair, JobFairRegistration
from ..institutions import InstitutionsMixin
from ..mixins import LinksMixin
from ..users import UserPublicMiniSerializer


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
