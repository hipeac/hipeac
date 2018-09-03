import json

from rest_framework import serializers
from rest_framework.relations import RelatedField

from hipeac.models import Metadata

"""
try:
    METADATA = dict([(m['id'], m) for m in Metadata.objects.values()])
except Exception as e:
    pass
"""


class JsonField(serializers.CharField):
    def to_internal_value(self, data):
        return json.dumps(data)

    def to_representation(self, obj):
        return json.loads(obj)


class MetadataListField(serializers.CharField):
    def to_internal_value(self, data):
        return ','.join([str(metadata['id']) for metadata in data])

    def to_representation(self, obj):
        METADATA = dict([(m['id'], m) for m in Metadata.objects.values()])
        return [] if obj == '' else [{
            'id': METADATA[int(pk)]['id'],
            'value': METADATA[int(pk)]['value']
        } for pk in obj.split(',')]


class MetadataField(RelatedField):
    queryset = Metadata.objects.all()
    pk_field = 'pk'

    def __init__(self, **kwargs):
        self.pk_field = kwargs.pop('pk_field', self.pk_field)
        RelatedField.__init__(self, **kwargs)

    def to_internal_value(self, data):
        return self.get_queryset().get(id=data['id'])

    def to_representation(self, obj):
        METADATA = dict([(m['id'], m) for m in Metadata.objects.values()])
        metadata = METADATA[getattr(obj, self.pk_field)]
        return {
            'id': metadata['id'],
            'value': metadata['value']
        }


class MetadataNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        exclude = []


class MetadataListSerializer(MetadataNestedSerializer):
    pass
