from django.template.response import TemplateResponse
from django.views.decorators.csrf import requires_csrf_token


@requires_csrf_token
def server_error(request):
    template_name = 'errors/500.html'
    context = {'request': request}
    return TemplateResponse(request, template_name, context, status=500)
