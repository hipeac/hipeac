from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.api.permissions import RegistrationPermission
from hipeac.api.serializers.events import (
    AcacesRegistrationSerializer,
    ConferenceRegistrationSerializer,
    CswRegistrationSerializer,
)
from hipeac.models import AcacesRegistration, ConferenceRegistration, CswRegistration, Event


class BaseRegistrationViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    pagination_class = None
    permission_classes = (RegistrationPermission,)

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        event = Event.objects.get(id=self.request.data["event"])

        if not event or not event.is_open_for_registration():
            raise ValidationError({"message": ["Registrations are closed for this event."]})

        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({"message": ["Duplicate entry - this user already has a registration."]})

    @method_decorator(never_cache)
    def list(self, request, *args, **kwargs):
        return ListModelMixin.list(self, request, *args, **kwargs)


class AcacesRegistrationViewSet(BaseRegistrationViewSet):
    queryset = AcacesRegistration.objects.all()
    serializer_class = AcacesRegistrationSerializer

    def set_accepted(self, value: bool) -> None:
        registration = self.get_object()

        if not registration.status == AcacesRegistration.STATUS_ADMITTED:
            raise ValidationError({"message": ["Registration status cannot be updated."]})

        registration.accepted = value
        registration.save()

    @action(detail=True, methods=["POST"])
    def accept(self, request, *args, **kwargs):
        self.set_accepted(True)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["POST"])
    def reject(self, request, *args, **kwargs):
        self.set_accepted(False)
        return super().retrieve(request, *args, **kwargs)


class ConferenceRegistrationViewSet(BaseRegistrationViewSet):
    queryset = ConferenceRegistration.objects.all()
    serializer_class = ConferenceRegistrationSerializer


class CswRegistrationViewSet(BaseRegistrationViewSet):
    queryset = CswRegistration.objects.all()
    serializer_class = CswRegistrationSerializer
