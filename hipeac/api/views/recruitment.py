from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from hipeac.models import Job, JobEvaluation
from ..permissions import HasAdminPermissionOrReadOnly
from ..serializers import JobNestedSerializer, JobSerializer, JobEvaluationSerializer


class JobViewSet(ModelViewSet):
    queryset = Job.objects.prefetch_related('employment_type', 'institution', 'project')
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = JobSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        self.queryset = Job.objects.active().prefetch_related('employment_type', 'institution', 'project') \
                                            .defer('description')
        self.pagination_class = None
        self.serializer_class = JobNestedSerializer
        return super().list(request, *args, **kwargs)


class JobEvaluationViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = JobEvaluation.objects.select_related('job')
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = JobEvaluationSerializer
