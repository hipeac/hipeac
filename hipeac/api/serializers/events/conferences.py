from rest_framework import serializers

from hipeac.models import Conference, ConferencePoster, ConferenceRegistration, ConferenceSponsor
from .newevents import EventSerializerMixin
from .registrations import RegistrationSerializer
from ..institutions import InstitutionNestedSerializer
from ..projects import ProjectNestedSerializer


class SponsorSerializer(serializers.ModelSerializer):
    institution = InstitutionNestedSerializer()
    project = ProjectNestedSerializer()

    class Meta:
        model = ConferenceSponsor
        exclude = ("conference",)


class ConferenceSerializer(EventSerializerMixin, serializers.ModelSerializer):
    sponsors = SponsorSerializer(many=True, read_only=True)

    class Meta:
        model = Conference
        exclude = ()


class ConferencePosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferencePoster
        exclude = ("registration",)


class ConferenceRegistrationSerializer(RegistrationSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:auth-registration-conference-detail", read_only=True)
    posters = ConferencePosterSerializer(many=True)

    class Meta(RegistrationSerializer.Meta):
        model = ConferenceRegistration
