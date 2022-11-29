from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet


from hipeac.models import JobFair, JobFairRegistration
from ...permissions import HasManagerPermission, HasManagerPermissionOrReadOnly
from ...serializers.recruitment import JobFairSerializer, JobFairRegistrationSerializer

# from ..serializers import SessionAccessLinkSerializer


class JobFairViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = JobFair.objects.all()
    permission_classes = (HasManagerPermissionOrReadOnly,)
    serializer_class = JobFairSerializer

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.prefetch_related("rel_institutions")
        return super().retrieve(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        serializer_class=JobFairSerializer,  # TODO: fix
    )
    def jobs(self, request, *args, **kwargs):
        self.queryset = self.get_object().registrations.prefetch_related(
            "rel_institutions__institution", "rel_projects__project"
        )
        return super().list(request, *args, **kwargs)


class JobFairRegistrationViewSet(
    ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = JobFairRegistration.objects.prefetch_related("jobs")
    pagination_class = None
    permission_classes = (HasManagerPermission,)
    serializer_class = JobFairRegistrationSerializer

    def get_queryset_for_fair(self):
        fair_id = self.request.query_params.get("fair_id", None)
        queryset = JobFairRegistration.objects.filter(user_id=self.request.user.id).prefetch_related("jobs")
        if fair_id is not None:
            queryset = queryset.filter(fair_id=fair_id)
        return queryset

    def perform_create(self, serializer):
        fair = JobFair.objects.get(id=self.request.data["fair"])

        if not fair or not fair.is_open_for_registration():
            raise ValidationError({"message": ["Registrations are closed for this job fair."]})

        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({"message": ["Duplicate entry - this user already has a registration."]})

    @method_decorator(never_cache)
    def list(self, request, *args, **kwargs):
        self.queryset = self.get_queryset_for_fair()
        return super().list(request, *args, **kwargs)

    @method_decorator(never_cache)
    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.get_queryset_for_fair()
        return super().retrieve(request, *args, **kwargs)
