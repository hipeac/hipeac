from rest_framework import serializers

from hipeac.models.cc import CC

from ..projects import ProjectListSerializer


class CCSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)

    class Meta:
        model = CC
        exclude = ()
