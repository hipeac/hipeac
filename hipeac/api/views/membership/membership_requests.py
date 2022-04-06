from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models.membership import MembershipRequest
from ...permissions import IsSteeringMember
from ...serializers import MembershipRequestListSerializer


class MembershipRequestViewSet(ListModelMixin, GenericViewSet):
    queryset = MembershipRequest.objects.pending().prefetch_related("files", "user__profile__institution")
    pagination_class = None
    permission_classes = (IsSteeringMember,)
    serializer_class = MembershipRequestListSerializer
