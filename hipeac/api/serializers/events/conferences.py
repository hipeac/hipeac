from rest_framework import serializers

from hipeac.models import Conference, ConferenceSponsor
from .newevents import EventSerializerMixin
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
