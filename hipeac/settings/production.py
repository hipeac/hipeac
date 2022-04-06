import os

from .base import *  # noqa


DEBUG = False

APP_DOMAIN = "hipeac.net"
ALLOWED_HOSTS = (os.environ.get("DJANGO_ALLOWED_HOST", "www.hipeac.net"),)
MEDIA_ROOT = "/storage/"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True

CRISPY_FAIL_SILENTLY = True


# sendfile

SENDFILE_ROOT = f"{MEDIA_ROOT}private"
SENDFILE_URL = "/-internal"


# https://docs.djangoproject.com/en/1.11/topics/cache/

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379"),
    },
    "staticfiles": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "django-staticfiles"},
}

CACHE_MIDDLEWARE_SECONDS = 20
USE_ETAGS = True


# http://celery.readthedocs.org/en/latest/django/

CELERY_BROKER_URL = os.environ.get("RABBITMQ_URL")


# https://docs.djangoproject.com/en/1.11/topics/email/

EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"

DEFAULT_FROM_EMAIL = f"HiPEAC <dev@{APP_DOMAIN}>"
SERVER_EMAIL = f"root@{APP_DOMAIN}"
EMAIL_SUBJECT_PREFIX = f"[{APP_DOMAIN}] "

ANYMAIL = {
    "MAILGUN_API_URL": os.environ.get("MAILGUN_API_URL", "https://api.eu.mailgun.net/v3"),
    "MAILGUN_API_KEY": os.environ.get("MAILGUN_API_KEY", "MAILGUN_API_KEY"),
    "MAILGUN_SEND_DEFAULTS": {
        "esp_extra": {
            "sender_domain": os.environ.get("MAILGUN_SENDER_DOMAIN", "MAILGUN_SENDER_DOMAIN"),
            "o:tag": "hipeac",
            "o:testmode": "no",
        }
    },
}


# https://docs.djangoproject.com/en/2.1/topics/logging/#django-security
# https://docs.sentry.io/platforms/python/?platform=python

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
}
