from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from hipeac.models import OpenEvent, OpenRegistration
from .generic import JsonField


class OpenEventSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)

    class Meta:
        model = OpenEvent
        exclude = ()
        lookup_field = 'uuid'


class OpenRegistrationSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True, required=False)
    fields = JsonField()

    class Meta:
        model = OpenRegistration
        exclude = ()
