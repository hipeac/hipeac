from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import ActionPoint, Meeting, MembershipRequest
from ..permissions import IsSteeringMember
from ..serializers import (
    ActionPointListSerializer, MeetingListSerializer, MeetingSerializer, MembershipRequestListSerializer
)


class ActionPointViewSet(ListModelMixin, GenericViewSet):
    queryset = ActionPoint.objects.pending().prefetch_related('attachments', 'owners__profile')
    pagination_class = None
    permission_classes = (IsSteeringMember,)
    serializer_class = ActionPointListSerializer


class MeetingViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Meeting.objects.all()
    pagination_class = None
    permission_classes = (IsSteeringMember,)
    serializer_class = MeetingListSerializer

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = MeetingSerializer
        return super().retrieve(request, *args, **kwargs)


class MembershipRequestViewSet(ListModelMixin, GenericViewSet):
    queryset = MembershipRequest.objects.pending().prefetch_related('attachments', 'user__profile__institution')
    pagination_class = None
    permission_classes = (IsSteeringMember,)
    serializer_class = MembershipRequestListSerializer
