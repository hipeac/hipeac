from django.contrib.auth import get_user_model
from django.urls import reverse
from django_countries.serializer_fields import CountryField
from drf_writable_nested import UniqueFieldsMixin, NestedUpdateMixin
from rest_framework import serializers

from hipeac.models import Profile, Project
from .generic import MetadataListField
from .institutions import InstitutionNestedSerializer


class ProfileSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()
    country = CountryField(country_dict=True)
    projects = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), many=True, allow_null=True)

    class Meta:
        model = Profile
        exclude = ('user',)


class ProfileNestedSerializer(ProfileSerializer):
    institution = InstitutionNestedSerializer()
    second_institution = InstitutionNestedSerializer()

    class Meta:
        model = Profile
        fields = ('country', 'bio', 'institution', 'second_institution', 'application_areas', 'topics')


class UserPublicListSerializer(serializers.ModelSerializer):
    profile = ProfileNestedSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='v1:user-detail')
    href = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('username', 'url', 'href', 'profile')

    def get_href(self, obj) -> str:
        return reverse('user', args=[obj.username])


class UserPublicSerializer(UserPublicListSerializer):
    pass


class AuthUserSerializer(NestedUpdateMixin, serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    profile = ProfileSerializer()

    class Meta:
        model = get_user_model()
        exclude = ('password', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
