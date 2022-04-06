from rest_framework import serializers

from hipeac.models import HipeacPartner
from .institutions import InstitutionNestedSerializer
from .users import UserPublicMiniSerializer


class HipeacPartnerNestedSerializer(serializers.ModelSerializer):
    institution = InstitutionNestedSerializer()
    representative = UserPublicMiniSerializer()

    class Meta:
        model = HipeacPartner
        exclude = ()


class HipeacPartnerListSerializer(HipeacPartnerNestedSerializer):
    pass
