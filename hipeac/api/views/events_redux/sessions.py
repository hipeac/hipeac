from http import HTTPStatus as status

from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from hipeac.models import AcacesRegistration, Event, Permission, Session
from hipeac.services.mailer import TemplateEmail

from ...permissions import HasManagerPermissionOrReadOnly, HasRegistrationForRelatedEvent, IsAuthenticated
from ...serializers import RegistrationListSerializer, SessionListSerializer, SessionSerializer, VideoListSerializer
from ..mixins import FilesMixin


class SessionViewSet(FilesMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Session.objects.all()
    pagination_class = None
    permission_classes = (HasManagerPermissionOrReadOnly,)
    serializer_class = SessionSerializer

    def list(self, request, *args, **kwargs):
        self.serializer_class = SessionListSerializer
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        permission_classes=(HasRegistrationForRelatedEvent,),
        serializer_class=RegistrationListSerializer,
    )
    def attendees(self, request, *args, **kwargs):
        session = self.get_object()
        self.queryset = session.registrations.select_related("user__profile").prefetch_related(
            "user__profile__institution"
        )

        if session.event.type == Event.ACACES:
            self.queryset = self.queryset.filter(
                acacesregistration__status=AcacesRegistration.STATUS_ADMITTED, acacesregistration__accepted=True
            )

        return super().list(request, *args, **kwargs)

    @action(detail=True, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = self.get_object().videos
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["POST"], permission_classes=(IsAuthenticated,))
    def contact(self, request, *args, **kwargs):
        """Send a messsage to session organizers."""

        organizers = self.get_object().acl.filter(level=Permission.ADMIN)

        try:
            email = TemplateEmail(
                email_code="events.session_organizers.contact",
                instance={  # TODO: this kwarg has the wrong name, no too extendable
                    "session": self.get_object(),
                    "sender_first_name": request.user.first_name,
                    "sender_name": request.user.profile.name,
                    "sender_affiliation": request.user.profile.institution,
                    "sender_email": request.user.email,
                    "message": request.data["message"],
                },
                to=[organizer.user.email for organizer in organizers],
            )
            email.send()

            return Response({"message": "Your message has been sent."})

        except Exception:
            return Response({"message": "We could not send your message."}, status=status.INTERNAL_SERVER_ERROR)
