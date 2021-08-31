from django.views.decorators.cache import never_cache
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models import OpenEvent, OpenRegistration
from ..serializers import OpenEventSerializer, OpenRegistrationSerializer


class OpenEventViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = OpenEvent.objects.all()
    serializer_class = OpenEventSerializer
    lookup_field = "code"

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=OpenRegistrationSerializer,
    )
    @never_cache
    def registrations(self, request, *args, **kwargs):
        secret = request.query_params.get("secret_key", False)
        if not secret or str(self.get_object().secret) != secret:
            raise PermissionDenied("Please include a valid `secret_key` query parameter in your request.")

        self.queryset = self.get_object().registrations
        return super().list(request, *args, **kwargs)


class OpenRegistrationViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = OpenRegistration.objects.all()
    serializer_class = OpenRegistrationSerializer
    lookup_field = "uuid"

    def create(self, request, *args, **kwargs):
        try:
            self.request.data["event"] = OpenEvent.objects.get(code=self.request.query_params.get("event", None)).id
        except OpenEvent.DoesNotExist:
            raise ValidationError({"event": ["Event does not exist."]})
        return super().create(request, *args, **kwargs)

    @never_cache
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
