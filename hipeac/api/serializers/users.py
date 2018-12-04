from django.contrib.auth import get_user_model
from django.urls import reverse
from django_countries.serializer_fields import CountryField
from drf_writable_nested import UniqueFieldsMixin, NestedUpdateMixin, WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Profile, Project
from .generic import LinkSerializer, MetadataListField
from .institutions import InstitutionNestedSerializer


class ProfileSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()
    links = LinkSerializer(required=False, many=True, allow_null=True)
    country = CountryField(country_dict=True)
    projects = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), many=True, allow_null=True)
    institution = InstitutionNestedSerializer()
    second_institution = InstitutionNestedSerializer()
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        exclude = ('user', 'is_bouncing', 'is_public', 'is_subscribed', 'meal_preference')


class ProfileNestedSerializer(ProfileSerializer):

    class Meta:
        model = Profile
        fields = ('name', 'country', 'institution', 'second_institution', 'application_areas', 'topics')


class UserPublicListSerializer(serializers.ModelSerializer):
    profile = ProfileNestedSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='v1:user-detail')
    href = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'url', 'href', 'profile')

    def get_href(self, obj) -> str:
        return reverse('user', args=[obj.username])


class UserPublicSerializer(UserPublicListSerializer):
    profile = ProfileSerializer()


class AuthUserSerializer(NestedUpdateMixin, serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    profile = ProfileSerializer()

    class Meta:
        model = get_user_model()
        exclude = ('password', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')


# Members
# -------

class MemberProfileSerializer(ProfileSerializer):
    institution = serializers.PrimaryKeyRelatedField(read_only=True)
    second_institution = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.CharField(read_only=True)
    membership_tags = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = ('name', 'country', 'institution', 'second_institution', 'application_areas', 'topics',
                  'membership_date', 'membership_tags', 'advisor_id')

    def get_membership_tags(self, obj):
        return obj.membership_tags.split(',')


class MemberPublicSerializer(UserPublicSerializer):
    profile = MemberProfileSerializer()
