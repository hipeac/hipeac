from rest_framework import serializers

from hipeac.models import Break


class BreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Break
        exclude = ("event",)
