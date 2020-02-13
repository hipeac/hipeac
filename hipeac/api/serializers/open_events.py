from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from hipeac.models import OpenEvent, OpenRegistration


class OpenEventSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)

    class Meta:
        model = OpenEvent
        exclude = ()
        lookup_field = 'uuid'


class OpenRegistrationSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True, required=False)

    class Meta:
        model = OpenRegistration
        exclude = ()
