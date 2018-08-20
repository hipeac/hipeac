from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic
from requests.auth import _basic_auth_str

from hipeac.models import MailingList


class DataSourceView(generic.View):
    """
    Displays a list of emails for different MailingLists.
    """

    def get(self, request, *args, **kwargs):
        code = kwargs.get('mailing_list')
        mailing_list = get_object_or_404(MailingList, code=code)

        if 'HTTP_AUTHORIZATION' in request.META:
            if request.META.get('HTTP_AUTHORIZATION') == _basic_auth_str(mailing_list.code, mailing_list.password):
                return HttpResponse('\n'.join(mailing_list.subscribers), content_type='text/plain; charset=utf-8')
            else:
                raise PermissionDenied

        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = f'Basic realm="Sympa {mailing_list}'
        return response
