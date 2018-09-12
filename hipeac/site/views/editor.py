from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views import generic


class EditorView(generic.TemplateView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_content_type(self, **kwargs):
        if not hasattr(self, 'ct'):
            self.ct = ContentType.objects.get(id=kwargs.get('ct', None))
        return self.ct

    def get_template_names(self):
        ct = self.get_content_type(**self.kwargs)
        return [''.join(['editor/', ct.model, '.html'])]

    def get_context_data(self, **kwargs):
        ct = self.get_content_type(**kwargs)
        context = super().get_context_data(**kwargs)
        context['obj_id'] = kwargs.get('pk', None)
        context['base_url'] = ''.join(['/api/v1', {
            'session': '/events/sessions/',
            'job': '/jobs/',
            'project': '/network/projects/',
            'institution': '/network/institutions/',
        }[ct.model]])
        return context
