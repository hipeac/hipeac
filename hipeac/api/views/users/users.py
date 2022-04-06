from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from hipeac.functions import send_task
from hipeac.site.emails.users import UserContactEmail

from hipeac.models import Publication, Video
from ...serializers import (
    UserPublicSerializer,
    UserPublicListSerializer,
    PublicationListSerializer,
    VideoListSerializer,
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
        self.queryset = Publication.objects.filter(rel_users__user_id=kwargs.get("pk"))
        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = Video.objects.filter(rel_users__user_id=kwargs.get("pk")).prefetch_related(
            "rel_application_areas__application_area", "rel_topics__topic"
        )
        return super().list(request, *args, **kwargs)


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
