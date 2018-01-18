from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views import generic
from requests.auth import _basic_auth_str

from .helpers import SympaGenerator


class DataSourceView(generic.View):
    """
    Displays a list of emails for different mailing lists.
    """

    def get(self, request, *args, **kwargs):
        mailing_list = kwargs.get('mailing_list')

        if 'HTTP_AUTHORIZATION' in request.META:
            if request.META.get('HTTP_AUTHORIZATION') == _basic_auth_str(settings.SYMPA_USER, settings.SYMPA_PASSWORD):
                subscribers = SympaGenerator().get_subscribers(mailing_list)
                return HttpResponse('\n'.join(subscribers), content_type='text/plain; charset=utf-8')
            else:
                raise PermissionDenied

        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="Sympa hipeac.%s"' % mailing_list
        return response
