from django.contrib.auth import get_user_model
from django_countries.serializer_fields import CountryField
from drf_writable_nested import UniqueFieldsMixin, NestedUpdateMixin, WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Profile, Project, Metadata
from ..mixins import ApplicationAreasMixin, LinksMixin, TopicsMixin


class AuthProfileSerializer(
    ApplicationAreasMixin, LinksMixin, TopicsMixin, UniqueFieldsMixin, WritableNestedModelSerializer
):
    country = CountryField(country_dict=True)
    projects = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), many=True, allow_null=True)
    name = serializers.CharField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)

    gender = serializers.PrimaryKeyRelatedField(queryset=Metadata.objects.all())
    meal_preference = serializers.PrimaryKeyRelatedField(queryset=Metadata.objects.all())

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
