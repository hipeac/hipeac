# https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/

import os

import sentry_sdk
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from sentry_sdk.integrations.django import DjangoIntegration
from whitenoise import WhiteNoise


env = os.environ.get("DJANGO_ENV", None)
if env in ["production"]:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN", "SENTRY_DSN"),
        release=os.environ.get("GIT_REV", None),
        environment=env,
        integrations=[DjangoIntegration()],
        ignore_errors=["django.security.DisallowedHost"],
        send_default_pii=True,
    )

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hipeac.settings")
os.environ["HTTPS"] = "on"

application = get_wsgi_application()
application = WhiteNoise(application, root=os.path.join(settings.SITE_ROOT, "www"), max_age=31536000)
