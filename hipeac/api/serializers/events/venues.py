from rest_framework import serializers

from hipeac.models import Room, Venue


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        exclude = ("venue",)


class VenueSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True)

    class Meta:
        model = Venue
        exclude = ("id", "country")
