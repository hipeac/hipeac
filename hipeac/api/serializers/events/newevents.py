from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from ..mixins import LinksMixin
from .breaks import BreakSerializer
from .sessions import SessionListSerializer
from .venues import VenueSerializer


class EventSerializerMixin(LinksMixin, metaclass=serializers.SerializerMetaclass):
    self = serializers.HyperlinkedIdentityField(view_name="v1:event-detail", read_only=True)
    href = serializers.CharField(source="get_absolute_url", read_only=True)
    country = CountryField(country_dict=True)
    name = serializers.CharField(read_only=True)
    images = serializers.DictField(read_only=True)
    dates = serializers.ListField()
    sessions = SessionListSerializer(many=True)
    breaks = BreakSerializer(many=True, read_only=True)
    is_early = serializers.BooleanField(read_only=True)
    is_open_for_registration = serializers.BooleanField(read_only=True)
    allows_payments = serializers.BooleanField(read_only=True)
    venue = VenueSerializer(read_only=True)
    extra_venues = VenueSerializer(many=True, read_only=True)
