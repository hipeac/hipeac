from django.contrib.auth import get_user_model
from django_countries.serializer_fields import CountryField
from drf_writable_nested import UniqueFieldsMixin, NestedUpdateMixin, WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Profile, Metadata
from ..institutions import InstitutionNestedSerializer
from ..mixins import ApplicationAreasMixin, FilesMixin, LinksMixin, TopicsMixin
from ..projects import ProjectsMixin


class AuthProfileSerializer(
    ApplicationAreasMixin,
    FilesMixin,
    LinksMixin,
    ProjectsMixin,
    TopicsMixin,
    UniqueFieldsMixin,
    WritableNestedModelSerializer,
):
    country = CountryField(country_dict=True)
    name = serializers.CharField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)
    institution = InstitutionNestedSerializer(allow_null=True)
    second_institution = InstitutionNestedSerializer(allow_null=True)

    gender = serializers.PrimaryKeyRelatedField(queryset=Metadata.objects.all(), allow_null=True)
    meal_preference = serializers.PrimaryKeyRelatedField(queryset=Metadata.objects.all(), allow_null=True)

    class Meta:
        model = Profile
        read_only_fields = ("image",)
        exclude = ("user", "is_bouncing", "is_public", "is_subscribed")


class AuthUserSerializer(NestedUpdateMixin, serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    profile = AuthProfileSerializer()

    class Meta:
        model = get_user_model()
        exclude = ("password", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")
