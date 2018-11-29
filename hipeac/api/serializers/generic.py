import json

from rest_framework import serializers
from rest_framework.relations import RelatedField

from hipeac.models import Image, Link, Metadata, get_cached_metadata, get_cached_metadata_queryset


class CustomChoiceField(serializers.ChoiceField):
    def to_representation(self, value):
        if value is None:
            return value
        return {
            'display': self.choices[value],
            'value': value,
        }


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image', 'position')


class JsonField(serializers.CharField):
    def to_internal_value(self, data):
        return json.dumps(data)

    def to_representation(self, obj):
        return json.loads(obj)


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ('type', 'url', 'id')


class MetadataListField(serializers.CharField):
    metadata = None

    def get_metadata(self):
        if not self.metadata:
            self.metadata = get_cached_metadata()
        return self.metadata

    def to_internal_value(self, data):
        return ','.join([str(metadata['id']) for metadata in data])

    def to_representation(self, obj):
        self.get_metadata()
        return [] if obj == '' else [{
            'id': self.metadata[int(pk)].id,
            'value': self.metadata[int(pk)].value
        } for pk in obj.split(',') if int(pk) in self.metadata]


class MetadataField(RelatedField):
    queryset = get_cached_metadata_queryset()
    pk_field = 'pk'

    def __init__(self, **kwargs):
        self.pk_field = kwargs.pop('pk_field', self.pk_field)
        RelatedField.__init__(self, **kwargs)

    def to_internal_value(self, data):
        return self.get_queryset().get(id=data['id'])

    def to_representation(self, obj):
        metadata = get_cached_metadata()[getattr(obj, self.pk_field)]
        return {
            'id': metadata.id,
            'value': metadata.value
        }


class MetadataNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        exclude = ()


class MetadataListSerializer(MetadataNestedSerializer):
    pass
