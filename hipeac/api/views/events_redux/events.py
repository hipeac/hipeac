from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet


class BaseEventViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "sessions__main_speaker__profile__institution",
                "sessions__rel_application_areas__application_area",
                "sessions__rel_topics__topic",
                "sessions__type",
            )
        )
