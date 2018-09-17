from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from rest_framework.relations import RelatedField

from hipeac.models import Institution
from .generic import LinkSerializer, MetadataListField


class InstitutionAllSerializer(serializers.ModelSerializer):
    short_name = serializers.CharField(read_only=True)

    class Meta:
        model = Institution
        fields = ('id', 'name', 'local_name', 'short_name', 'type')


class InstitutionNestedSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)
    url = serializers.HyperlinkedIdentityField(view_name='v1:institution-detail', read_only=True)
    href = serializers.CharField(source='get_absolute_url', read_only=True)
    short_name = serializers.CharField(read_only=True)

    class Meta:
        model = Institution
        read_only_fields = ('image', 'images')
        fields = ['id', 'name', 'local_name', 'short_name', 'images', 'url', 'href', 'location', 'country', 'type']


class InstitutionListSerializer(InstitutionNestedSerializer):
    application_areas = MetadataListField()

    class Meta(InstitutionNestedSerializer.Meta):
        fields = InstitutionNestedSerializer.Meta.fields + ['application_areas']


class InstitutionSerializer(InstitutionNestedSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()
    slug = serializers.CharField(read_only=True)
    links = LinkSerializer(read_only=True, many=True)
    children = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    open_positions = serializers.SerializerMethodField(read_only=True)

    class Meta(InstitutionNestedSerializer.Meta):
        fields = InstitutionNestedSerializer.Meta.fields + [
            'application_areas', 'topics', 'parent', 'children', 'slug', 'open_positions', 'description', 'links'
        ]

    def get_open_positions(self, obj):
        from .recruitment import JobNestedSerializer  # noqa
        jobs = obj.jobs.active().defer('description')
        return JobNestedSerializer(jobs, many=True, context=self.context).data
