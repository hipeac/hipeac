from rest_framework.viewsets import ModelViewSet

from hipeac.models import Job
from ..serializers import JobNestedSerializer, JobSerializer


class JobViewSet(ModelViewSet):
    queryset = Job.objects.active().prefetch_related('employment_type', 'institution', 'project')
    serializer_class = JobSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.defer('description')
        self.pagination_class = None
        self.serializer_class = JobNestedSerializer
        return super().list(request, *args, **kwargs)
