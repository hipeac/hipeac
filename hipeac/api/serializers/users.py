from django.contrib.auth import get_user_model
from django.urls import reverse
from django_countries.serializer_fields import CountryField
from drf_writable_nested import UniqueFieldsMixin, NestedUpdateMixin, WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Profile, Project
from .generic import LinkSerializer, MetadataField, MetadataListField
from .institutions import InstitutionMiniSerializer


class ProfileSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()
    links = LinkSerializer(required=False, many=True, allow_null=True)
    country = CountryField(country_dict=True)
    projects = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), many=True, allow_null=True)
    name = serializers.CharField(read_only=True)
    membership_tags = serializers.SerializerMethodField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)
    meal_preference = MetadataField(allow_null=True)

    class Meta:
        model = Profile
        exclude = ('user', 'is_bouncing', 'is_public', 'is_subscribed')

    def get_membership_tags(self, obj):
        return obj.membership_tags.split(',') if obj.membership_tags else []


class ProfileMiniSerializer(ProfileSerializer):
    name = serializers.CharField(read_only=True)
    institution = InstitutionMiniSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ('name', 'country', 'institution', 'avatar_url')


class ProfileMembershipSerializer(ProfileSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ('name', 'institution', 'advisor')


class ProfileNestedSerializer(ProfileSerializer):
    institution = InstitutionMiniSerializer(read_only=True)
    second_institution = InstitutionMiniSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ('name', 'country', 'institution', 'second_institution', 'membership_date', 'membership_tags',
                  'application_areas', 'topics', 'avatar_url')


# Users
# -----


class UserPublicSerializer(serializers.ModelSerializer):
    profile = ProfileNestedSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='v1:user-detail')
    href = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'url', 'href', 'profile')

    def get_href(self, obj) -> str:
        return reverse('user', args=[obj.username]) if obj.profile.is_public else None


class UserPublicMiniSerializer(UserPublicSerializer):
    profile = ProfileMiniSerializer()


class UserPublicMembershipSerializer(UserPublicSerializer):
    profile = ProfileMembershipSerializer()


class UserPublicListSerializer(UserPublicSerializer):
    profile = ProfileNestedSerializer()


class AuthUserSerializer(NestedUpdateMixin, serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    profile = ProfileSerializer()

    class Meta:
        model = get_user_model()
        exclude = ('password', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
