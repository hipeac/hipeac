from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from sentry_sdk import last_event_id


@requires_csrf_token
def permission_denied_error(request, exception):
    return render(request, 'errors/403.html', {
        'exception': exception,
    }, status=403)


@requires_csrf_token
def server_error(request):
    return render(request, 'errors/500.html', {
        'sentry_event_id': last_event_id(),
    }, status=500)
