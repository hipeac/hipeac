from django_countries.serializer_fields import CountryField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Institution
from .generic import LinkSerializer, MetadataListField


class InstitutionSerializer(WritableNestedModelSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()
    links = LinkSerializer(many=True)
    children = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    country = CountryField(country_dict=True)
    short_name = serializers.CharField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='v1:institution-detail', read_only=True)
    href = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Institution
        read_only_fields = ('image', 'images')
        exclude = ('colloquial_name',)


class InstitutionMiniSerializer(InstitutionSerializer):

    class Meta:
        model = Institution
        fields = ('id', 'type', 'name', 'local_name', 'short_name', 'country', 'href')


class InstitutionNestedSerializer(InstitutionSerializer):

    class Meta():
        model = Institution
        fields = ('id', 'type', 'name', 'local_name', 'short_name', 'location', 'country', 'url', 'href', 'images')


class InstitutionListSerializer(InstitutionNestedSerializer):
    pass
