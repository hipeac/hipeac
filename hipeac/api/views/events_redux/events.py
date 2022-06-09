from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet


class BaseEventViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related(
            "sessions__main_speaker__profile__institution",
            "sessions__rel_application_areas__application_area",
            "sessions__rel_topics__topic",
            "sessions__type",
            "sponsors__institution",
        )
        return super().retrieve(request, *args, **kwargs)
