from rest_framework import serializers

from hipeac.models import Vision


class VisionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vision
        fields = '__all__'
