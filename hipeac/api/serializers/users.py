from django.contrib.auth import get_user_model
from django.urls import reverse
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from hipeac.models import Profile
from .generic import MetadataListField
from .institutions import InstitutionRelatedField


class ProfileNestedSerializer(serializers.ModelSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()
    country = CountryField(country_dict=True)
    institution = InstitutionRelatedField()
    second_institution = InstitutionRelatedField()

    class Meta:
        model = Profile
        fields = ['country', 'bio', 'institution', 'second_institution', 'application_areas', 'topics']


class UserPublicListSerializer(serializers.ModelSerializer):
    profile = ProfileNestedSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='v1:user-detail')
    href = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['username', 'url', 'href', 'profile']

    def get_href(self, obj) -> str:
        return reverse('user', args=[obj.username])


class UserPublicSerializer(UserPublicListSerializer):
    pass
