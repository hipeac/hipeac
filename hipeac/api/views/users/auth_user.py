from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..mixins import FilesMixin
from ...serializers import (
    AuthUserSerializer,
    NotificationSerializer,
    WebinarRegistrationListSerializer,
)


class AuthUserViewSet(FilesMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = AuthUserSerializer

    def get_queryset(self):
        return (
            get_user_model()
            .objects.select_related(
                "profile__gender",
                "profile__meal_preference",
                "profile__position",
                "profile__institution",
                "profile__second_institution",
            )
            .prefetch_related(
                "profile__files",
                "profile__links",
                "profile__rel_application_areas__application_area",
                "profile__rel_projects__project",
                "profile__rel_topics__topic",
            )
        )

    def get_object(self):
        return self.get_queryset().get(pk=self.request.user.pk)

    @action(methods=["get", "patch", "put"], detail=False, serializer_class=AuthUserSerializer)
    @method_decorator(never_cache)
    def account(self, request, *args, **kwargs):
        return {"get": self.retrieve, "patch": self.partial_update, "put": self.update}[request.method.lower()](
            request, *args, **kwargs
        )

    @action(methods=["get"], detail=False)
    def notifications(self, request, *args, **kwargs):
        notifications = request.user.notifications.active()
        return Response(NotificationSerializer(notifications, many=True).data)

    @action(methods=["get"], detail=False)
    def webinars(self, request, *args, **kwargs):
        webinars = request.user.webinarregistration_registrations.upcoming()
        return Response(WebinarRegistrationListSerializer(webinars, many=True).data)
