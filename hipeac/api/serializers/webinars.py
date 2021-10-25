from rest_framework import serializers

from hipeac.models import Webinar, WebinarRegistration
from .generic import MetadataFieldWithPosition, MetadataListField


class WebinarListSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:webinar-detail", read_only=True)
    rel_attendees = serializers.HyperlinkedIdentityField(view_name="v1:webinar-attendees")
    rel_register = serializers.HyperlinkedIdentityField(view_name="v1:webinar-register")
    rel_unregister = serializers.HyperlinkedIdentityField(view_name="v1:webinar-unregister")
    session_type = MetadataFieldWithPosition()
    application_areas = MetadataListField()
    topics = MetadataListField()
    keywords = serializers.JSONField(read_only=True)

    class Meta:
        model = Webinar
        exclude = ("updated_at",)
        lookup_field = "pk"


class WebinarRegistrationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebinarRegistration
        exclude = ("updated_at",)
        lookup_field = "pk"
