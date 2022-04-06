from rest_framework import serializers

from hipeac.models import ActionPoint, Meeting
from .mixins import FilesMixin


class ActionPointListSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    class Meta:
        model = ActionPoint
        exclude = ("description",)

    def get_users(self, obj):
        return [u.profile.name for u in obj.owners]


class MeetingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        exclude = ("description",)


class MeetingSerializer(FilesMixin, serializers.ModelSerializer):
    class Meta:
        model = Meeting
        exclude = ()
