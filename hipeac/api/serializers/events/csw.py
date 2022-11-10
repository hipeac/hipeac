from rest_framework import serializers

from hipeac.models import Csw, CswRegistration
from .newevents import EventSerializerMixin
from .registrations import RegistrationSerializer


class CswSerializer(EventSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Csw
        exclude = ()


class CswRegistrationSerializer(RegistrationSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:auth-registration-csw-detail", read_only=True)

    class Meta(RegistrationSerializer.Meta):
        model = CswRegistration
