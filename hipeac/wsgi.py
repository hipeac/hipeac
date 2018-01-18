"""
WSGI config for the project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hipeac.settings')
os.environ['HTTPS'] = 'on'

application = get_wsgi_application()
application = WhiteNoise(application, root=os.path.join(settings.SITE_ROOT, 'www'), max_age=31536000)
