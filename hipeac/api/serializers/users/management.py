from django.contrib.auth import get_user_model
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from hipeac.models import Profile
from ..institutions import InstitutionMiniSerializer
from ..metadata import MetadataSerializer


class ProfileManagementSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)
    name = serializers.CharField(read_only=True)
    institution = InstitutionMiniSerializer(read_only=True)
    gender = MetadataSerializer(allow_null=True)
    meal_preference = MetadataSerializer(allow_null=True)

    class Meta:
        model = Profile
        fields = ("name", "country", "institution", "gender", "meal_preference")


class UserManagementSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    profile = ProfileManagementSerializer()

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "date_joined", "last_login", "profile")
