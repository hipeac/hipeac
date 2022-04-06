from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import ActionPoint, Meeting
from ..permissions import IsSteeringMember
from ..serializers import (
    ActionPointListSerializer,
    MeetingListSerializer,
    MeetingSerializer,
)


class ActionPointViewSet(ListModelMixin, GenericViewSet):
    queryset = ActionPoint.objects.pending().prefetch_related("files", "rel_users__user__profile")
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
