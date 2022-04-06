from rest_framework import serializers

from hipeac.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("type", "file", "description")
