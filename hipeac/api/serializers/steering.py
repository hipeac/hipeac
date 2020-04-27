from rest_framework import serializers

from hipeac.models import ActionPoint, Meeting, MembershipRequest
from .generic import PrivateFileSerializer
from .users import UserPublicMiniSerializer


class ActionPointListSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    class Meta:
        model = ActionPoint
        exclude = ("description", "owners")

    def get_users(self, obj):
        return [u.profile.name for u in obj.owners.all()]


class MeetingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        exclude = ("description",)


class MeetingSerializer(serializers.ModelSerializer):
    attachments = PrivateFileSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        exclude = ()


class MembershipRequestListSerializer(serializers.ModelSerializer):
    user = UserPublicMiniSerializer()
    attachments = PrivateFileSerializer(many=True, read_only=True)

    class Meta:
        model = MembershipRequest
        exclude = ()
