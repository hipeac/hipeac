from rest_framework import serializers

from hipeac.models import Notification
from hipeac.tools.notifications.generic import parse_notification


class NotificationSerializer(serializers.ModelSerializer):
    data = serializers.DictField(read_only=True)
    message = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        exclude = ()

    def get_message(self, obj):
        return parse_notification(obj)
