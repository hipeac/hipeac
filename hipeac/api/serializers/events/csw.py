from rest_framework import serializers

from hipeac.models import Csw
from .newevents import EventSerializerMixin


class CswSerializer(EventSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Csw
        exclude = ()
