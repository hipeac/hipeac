from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from rest_framework.relations import RelatedField

from hipeac.models import Institution
from .generic import MetadataListField


class InstitutionNestedSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)
    url = serializers.HyperlinkedIdentityField(view_name='v1:institution-detail', read_only=True)
    href = serializers.CharField(source='get_absolute_url', read_only=True)
    short_name = serializers.CharField(read_only=True)

    class Meta:
        model = Institution
        read_only_fields = ['image', 'images']
        fields = ['id', 'name', 'local_name', 'short_name', 'images', 'url', 'href', 'location', 'country', 'type']


class InstitutionRelatedField(RelatedField):
    queryset = Institution.objects.all()

    def to_internal_value(self, data):
        return self.get_queryset().get(id=data['id'])

    def to_representation(self, obj):
        return InstitutionNestedSerializer(obj, context=self.context).data


class InstitutionListSerializer(InstitutionNestedSerializer):
    application_areas = MetadataListField()

    class Meta(InstitutionNestedSerializer.Meta):
        fields = InstitutionNestedSerializer.Meta.fields + ['application_areas']


class InstitutionSerializer(InstitutionNestedSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()
    parent = InstitutionRelatedField(required=False, allow_null=True)
    children = InstitutionRelatedField(many=True, required=False)
    slug = serializers.CharField(read_only=True)

    open_positions = serializers.SerializerMethodField()

    class Meta(InstitutionNestedSerializer.Meta):
        fields = InstitutionNestedSerializer.Meta.fields + [
            'application_areas', 'topics', 'parent', 'children', 'slug', 'open_positions', 'description'
        ]

    def get_open_positions(self, obj):
        from .recruitment import JobNestedSerializer  # noqa
        jobs = obj.jobs.active().defer('description')
        return JobNestedSerializer(jobs, many=True, context=self.context).data
