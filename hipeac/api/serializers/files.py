from rest_framework import serializers

from hipeac.models import File


class FileSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:file-detail")
    url = serializers.FileField(source="file")

    class Meta:
        model = File
        fields = ("self", "url")
