from django.db import IntegrityError
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from hipeac.models import Webinar, WebinarRegistration
from hipeac.services.zoom import Zoomer
from ..permissions import HasRegistrationForWebinar
from ..serializers import RegistrationListSerializer, WebinarListSerializer, WebinarRegistrationListSerializer


class WebinarViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    pagination_class = None
    serializer_class = WebinarListSerializer
    queryset = Webinar.objects.all()

    @action(
        detail=True,
        pagination_class=None,
        permission_classes=(HasRegistrationForWebinar,),
        serializer_class=RegistrationListSerializer,
    )
    def attendees(self, request, *args, **kwargs):
        self.queryset = (
            self.get_object()
            .registrations.select_related("user__profile")
            .prefetch_related("user__profile__institution")
        )
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["POST"],
        pagination_class=None,
        permission_classes=(IsAuthenticated,),
        serializer_class=WebinarRegistrationListSerializer,
    )
    def register(self, request, *args, **kwargs):
        webinar = self.get_object()
        profile = request.user.profile
        access_link = None

        if webinar.zoom_webinar_int:
            user_data = {
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "country": profile.country.code if profile.country else None,
            }
            access_link = Zoomer().post_webinar_registrant(webinar.zoom_webinar_int, user_data)

        try:
            WebinarRegistration.objects.create(webinar_id=webinar.id, user_id=request.user.id, access_link=access_link)
        except IntegrityError:
            raise PermissionDenied({"message": ["You are already registered for this webinar."]})

        self.queryset = request.user.webinar_registrations.upcoming()
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["POST"],
        pagination_class=None,
        permission_classes=(HasRegistrationForWebinar,),
        serializer_class=WebinarRegistrationListSerializer,
    )
    def unregister(self, request, *args, **kwargs):
        try:
            registration = self.get_object().registrations.get(user_id=request.user.id)
            registration.delete()
            self.queryset = request.user.webinar_registrations.upcoming()
            return super().list(request, *args, **kwargs)
        except WebinarRegistration.DoesNotExist:
            raise PermissionDenied({"message": ["You are not registered for this webinar."]})
