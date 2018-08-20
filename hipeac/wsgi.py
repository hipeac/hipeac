# https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/

import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hipeac.settings')
os.environ['HTTPS'] = 'on'

app = get_wsgi_application()
app = WhiteNoise(app, root=os.path.join(settings.SITE_ROOT, 'www'), max_age=31536000)
