from rest_framework import serializers

from hipeac.models import Webinar, WebinarRegistration
from ..metadata import MetadataSerializer


class WebinarSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:webinar-detail", read_only=True)
    rel_attendees = serializers.HyperlinkedIdentityField(view_name="v1:webinar-attendees")
    rel_register = serializers.HyperlinkedIdentityField(view_name="v1:webinar-register")
    rel_unregister = serializers.HyperlinkedIdentityField(view_name="v1:webinar-unregister")
    type = MetadataSerializer()
    application_areas = MetadataSerializer(many=True)
    topics = MetadataSerializer(many=True)
    keywords = serializers.JSONField(read_only=True)

    class Meta:
        model = Webinar
        exclude = ("created_at", "updated_at", "zoom_attendee_report")


class WebinarRegistrationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebinarRegistration
        exclude = ("updated_at",)
