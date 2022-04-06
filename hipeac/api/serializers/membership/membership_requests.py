from rest_framework import serializers

from hipeac.models.membership import MembershipRequest
from ..mixins import FilesMixin
from ..users import UserPublicMiniSerializer


class MembershipRequestListSerializer(FilesMixin, serializers.ModelSerializer):
    user = UserPublicMiniSerializer()

    class Meta:
        model = MembershipRequest
        exclude = ()
