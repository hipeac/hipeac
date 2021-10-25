from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from hipeac.functions import send_task
from hipeac.site.emails.users import UserContactEmail

from hipeac.models import Profile, Video
from ..serializers import (
    AuthUserSerializer,
    UserPublicSerializer,
    UserPublicListSerializer,
    NotificationSerializer,
    PublicationListSerializer,
    VideoListSerializer,
    WebinarRegistrationListSerializer,
)


class UserViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = (
        get_user_model()
        .objects.filter(is_active=True)
        .select_related("profile__institution")
        .prefetch_related("profile__second_institution")
    )
    serializer_class = UserPublicSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer("profile__bio")
        self.serializer_class = UserPublicListSerializer
        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=PublicationListSerializer)
    def publications(self, request, *args, **kwargs):
        self.queryset = Profile.objects.get(user_id=kwargs.get("pk")).publications.all()
        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = Video.objects.filter(users__in=[kwargs.get("pk")])
        return super().list(request, *args, **kwargs)


class AuthUserViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = AuthUserSerializer

    def get_object(self):
        return self.request.user

    @action(methods=["get", "patch", "put"], detail=False, serializer_class=AuthUserSerializer)
    @never_cache
    def account(self, request, *args, **kwargs):
        return {"get": self.retrieve, "patch": self.partial_update, "put": self.update}[request.method.lower()](
            request, *args, **kwargs
        )

    @action(detail=False, pagination_class=None, serializer_class=NotificationSerializer)
    def notifications(self, request, *args, **kwargs):
        self.queryset = request.user.notifications.active()
        return ListModelMixin.list(self, request, *args, **kwargs)

    @action(detail=False, pagination_class=None, serializer_class=WebinarRegistrationListSerializer)
    def webinars(self, request, *args, **kwargs):
        self.queryset = request.user.webinar_registrations.upcoming()
        return ListModelMixin.list(self, request, *args, **kwargs)


class ContactUser(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Send a message to a HiPEAC user.
        """
        try:
            email = UserContactEmail(
                instance={
                    "user": User.objects.get(id=self.request.data["user_id"]),
                    "sender": self.request.user,
                    "message": self.request.data["message"],
                }
            )
            send_task("hipeac.tasks.emails.send_from_template", email.data)

            return Response({"message": "Your message has been sent."})

        except Exception:
            return Response({"message": "We could not send your message."}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
