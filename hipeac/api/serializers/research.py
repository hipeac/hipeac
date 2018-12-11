from rest_framework import serializers

from hipeac.models import Publication, PublicationConference
from .generic import CustomChoiceField


class PublicationConferenceListSerializer(serializers.ModelSerializer):
    acronym = CustomChoiceField(choices=PublicationConference.CONFERENCES)

    class Meta:
        model = PublicationConference
        fields = '__all__'


class PublicationSerializer(serializers.ModelSerializer):
    conference = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Publication
        exclude = ()

    def get_conference(self, obj) -> str:
        return str(obj.conference) if obj.conference else None


class PublicationListSerializer(PublicationSerializer):

    class Meta:
        model = Publication
        exclude = ('authors',)
