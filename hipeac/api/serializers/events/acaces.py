from rest_framework import serializers

from hipeac.models import (
    Acaces,
    AcacesBus,
    AcacesCourse,
    AcacesCourseSession,
    AcacesGrant,
    AcacesPoster,
    AcacesRegistration,
)
from .newevents import EventSerializerMixin
from .registrations import RegistrationSerializer
from ..metadata import MetadataSerializer
from ..mixins import FilesMixin, LinksMixin
from ..users import UserPublicMiniSerializer, UserManagementSerializer


class AcacesGrantSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:acaces-grant-management-detail", read_only=True)

    class Meta:
        model = AcacesGrant
        read_only_fields = ("country",)
        exclude = ("id", "event")


class AcacesBusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcacesBus
        exclude = ()


class AcacesPosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcacesPoster
        read_only_fields = ("abstract", "poster", "position")
        exclude = ("registration",)


class AcacesSerializer(EventSerializerMixin, serializers.ModelSerializer):
    buses = AcacesBusSerializer(many=True, read_only=True)
    grants = AcacesGrantSerializer(many=True, read_only=True)

    class Meta:
        model = Acaces
        exclude = ()


class AcacesCourseSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcacesCourseSession
        exclude = ("course",)


class AcacesCourseSerializer(FilesMixin, LinksMixin, serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:course-detail", read_only=True)
    sessions = AcacesCourseSessionSerializer(many=True)
    teachers = UserPublicMiniSerializer(many=True, read_only=True)
    topics = MetadataSerializer(many=True, read_only=True)

    class Meta:
        model = AcacesCourse
        exclude = ()


class AcacesRegistrationSerializer(RegistrationSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:auth-registration-acaces-detail", read_only=True)
    user = UserManagementSerializer(read_only=True)
    poster = AcacesPosterSerializer(allow_null=True)

    class Meta(RegistrationSerializer.Meta):
        model = AcacesRegistration
        read_only_fields = RegistrationSerializer.Meta.read_only_fields + (
            "status",
            "accepted",
            "grant_assigned",
            "assigned_hotel",
            "roommate",
            "gelato",
        )


class AcacesRegistrationManagementSerializer(AcacesRegistrationSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:acaces-registration-management-detail", read_only=True)
    grants = serializers.SerializerMethodField(read_only=True)

    class Meta(AcacesRegistrationSerializer.Meta):
        read_only_fields = RegistrationSerializer.Meta.read_only_fields + (
            "assigned_hotel",
            "roommate",
            "gelato",
        )

    def get_grants(self, obj):
        return (
            date.year
            for date in AcacesRegistration.objects.filter(user_id=obj.user_id, grant_assigned=True, accepted=True)
            .exclude(event_id=obj.event_id)
            .values_list("created_at", flat=True)
        )
