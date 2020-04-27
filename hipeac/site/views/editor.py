from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views import generic


class EditorBaseView(generic.TemplateView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return ["".join(["editor/", self.get_model_name(**self.kwargs), ".html"])]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["obj_id"] = kwargs.get("pk", None)
        context["base_url"] = "".join(
            [
                "/api/v1",
                {
                    "session": "/events/sessions/",
                    "job": "/jobs/",
                    "jobevaluation": "/jobs/evaluations/",
                    "project": "/network/projects/",
                    "institution": "/network/institutions/",
                }[self.get_model_name(**kwargs)],
            ]
        )
        return context


class EditorView(EditorBaseView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object(**kwargs)
        if not request.user.is_staff and not obj.can_be_managed_by(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, **kwargs):
        if not hasattr(self, "object"):
            ct = ContentType.objects.get(id=kwargs.get("ct", None))
            self.object = ct.get_object_for_this_type(pk=kwargs.get("pk", None))
        return self.object

    def get_model_name(self, **kwargs):
        if not hasattr(self, "model_name"):
            ct = ContentType.objects.get(id=kwargs.get("ct", None))
            self.model_name = ct.model
        return self.model_name


class EditorCreateView(EditorBaseView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_model_name(self, **kwargs):
        if not hasattr(self, "model_name"):
            self.model_name = self.kwargs.get("model", None)
        return self.model_name
