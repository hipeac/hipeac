from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from hipeac.models import Job, JobEvaluation, Video
from hipeac.models.recruitment import validate_institution
from ...permissions import HasAdminPermissionOrReadOnly
from ...serializers import JobNestedSerializer, JobSerializer, JobEvaluationSerializer, VideoListSerializer


class JobViewSet(ModelViewSet):
    queryset = Job.objects.all()
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = JobSerializer
    http_method_names = [
        "get",
        "post",
        "put",
        "delete",
        "head",
        "options",
        "trace",
    ]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def _validate(self, request, *args, **kwargs):
        try:
            validate_institution(request.data.get("institution"), request.user)
        except Exception as e:
            raise ValidationError({"institution": [str(e)]})

        if request.data.get("email", "") == "" and not request.data.get("links"):
            raise ValidationError({"contact_data": ["Please add an email or related website."]})

    def create(self, request, *args, **kwargs):
        self._validate(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._validate(request)
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.queryset = Job.objects.active().defer("description")
        self.pagination_class = None
        self.serializer_class = JobNestedSerializer
        return super().list(request, *args, **kwargs)

    @action(detail=False, pagination_class=None, serializer_class=VideoListSerializer)
    def videos(self, request, *args, **kwargs):
        self.queryset = Video.objects.filter(type="jobs")
        return super().list(request, *args, **kwargs)


class JobEvaluationViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = JobEvaluation.objects.select_related("job")
    permission_classes = (HasAdminPermissionOrReadOnly,)
    serializer_class = JobEvaluationSerializer
