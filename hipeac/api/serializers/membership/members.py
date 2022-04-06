from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from hipeac.models.membership import Member
from ..institutions import InstitutionMiniSerializer


class MemberSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)
    institution = InstitutionMiniSerializer()
    second_institution = InstitutionMiniSerializer()
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = Member
        exclude = ()
