from rest_framework import serializers

from hipeac.models import File
from .mixins import KeywordsMixin


class FileSerializer(KeywordsMixin, serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:file-detail")
    url = serializers.FileField(source="file")

    class Meta:
        model = File
        fields = ("self", "type", "url", "description", "keywords")
