import os

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import urlquote
from django.views.generic import View
from mimetypes import guess_type

from hipeac.models import Vision


class SendfileView(View):
    """
    Serves `private` assets.
    """
    def get_path_and_filename(self, *args, **kwargs):
        return kwargs.get('path'), kwargs.get('filename')

    def get(self, request, *args, **kwargs):
        path, filename = self.get_path_and_filename(*args, **kwargs)
        response = HttpResponse()
        url = f'{settings.SENDFILE_URL}{path}{filename}'
        guessed_mimetype, guessed_encoding = guess_type(filename)

        response['X-Accel-Redirect'] = url.encode('utf-8')
        response['Content-Type'] = guessed_mimetype if guessed_mimetype else 'application/octet-stream'
        response['Content-length'] = os.path.getsize(f'{settings.SENDFILE_ROOT}{path}{filename}')
        response['Content-Disposition'] = 'attachment; filename={}'.format(urlquote(filename))
        if guessed_encoding:
            response['Content-Encoding'] = guessed_encoding

        return response


class FirewallView(SendfileView):
    """
    Serves `private` assets, checking staff permissions beforehand.
    """
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied


class VisionDownload(SendfileView):
    """
    Serves `private` vision files, but records downloads first.
    """
    def get_path_and_filename(self, *args, **kwargs):
        vision = get_object_or_404(Vision, publication_date__year=kwargs.get('year'))

        vision_file = vision.file if vision.file else vision.file_draft
        vision.downloads = F('downloads') + 1
        vision.save()

        path, filename = os.path.split(vision_file.name.replace('private/', '/'))

        return f'{path}/', filename
