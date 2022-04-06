from rest_framework import serializers

from hipeac.models import Image


class CustomChoiceField(serializers.ChoiceField):
    def to_representation(self, value):
        if value is None:
            return value
        return {
            "display": self.choices[value],
            "value": value,
        }


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image", "position")
