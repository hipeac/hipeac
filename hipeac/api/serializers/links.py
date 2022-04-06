from rest_framework import serializers

from hipeac.models import Link


class LinkSerializer(serializers.ModelSerializer):
    type_display = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = ("id", "url", "type", "type_display")

    def get_type_display(self, obj) -> str:
        return obj.get_type_display()
