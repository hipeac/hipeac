from django.contrib.auth import get_user_model
from django.urls import reverse
from django_countries.serializer_fields import CountryField
from drf_writable_nested import UniqueFieldsMixin, WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Profile, Project
from ..institutions import InstitutionMiniSerializer
from ..metadata import MetadataSerializer
from ..mixins import ApplicationAreasMixin, LinksMixin, TopicsMixin


class ProfileSerializer(ApplicationAreasMixin, LinksMixin, UniqueFieldsMixin, WritableNestedModelSerializer):
    country = CountryField(country_dict=True)
    projects = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), many=True, allow_null=True)
    name = serializers.CharField(read_only=True)
    # membership_tags = serializers.SerializerMethodField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)
    meal_preference = MetadataSerializer(allow_null=True)

    class Meta:
        model = Profile
        read_only_fields = ("image",)
        exclude = ("user", "is_bouncing", "is_public", "is_subscribed")

    def get_membership_tags(self, obj):
        return obj.membership_tags.split(",") if obj.membership_tags else []


class ProfileMiniSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)
    name = serializers.CharField(read_only=True)
    institution = InstitutionMiniSerializer(read_only=True)
    avatar_url = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ("name", "country", "institution", "avatar_url", "bio")


class ProfileMembershipSerializer(TopicsMixin, ProfileSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ("name", "institution", "second_institution", "advisor", "topics")


class ProfileNestedSerializer(TopicsMixin, ProfileSerializer):
    institution = InstitutionMiniSerializer(read_only=True)
    second_institution = InstitutionMiniSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "name",
            "country",
            "institution",
            "second_institution",
            "application_areas",
            "topics",
            "avatar_url",
        )


class ProfilePublicSerializer(ProfileNestedSerializer):
    class Meta:
        model = Profile
        fields = (
            "bio",
            "name",
            "country",
            "institution",
            "second_institution",
            "application_areas",
            "topics",
            "links",
            "avatar_url",
        )


# Users
# -----


class UserPublicSerializer(serializers.ModelSerializer):
    profile = ProfilePublicSerializer()
    url = serializers.HyperlinkedIdentityField(view_name="v1:user-detail")
    href = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "url", "href", "profile")

    def get_href(self, obj) -> str:
        return reverse("user", args=[obj.username]) if obj.profile.is_public else None


class UserPublicMiniSerializer(UserPublicSerializer):
    profile = ProfileMiniSerializer()


class UserPublicMembershipSerializer(UserPublicSerializer):
    profile = ProfileMembershipSerializer()


class UserPublicListSerializer(UserPublicSerializer):
    profile = ProfileNestedSerializer()


class UserOnlySerializer(UserPublicSerializer):
    profile = None

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name")
