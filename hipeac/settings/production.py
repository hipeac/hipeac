import os

from urllib.parse import urlparse

from .base import *  # noqa


DEBUG = False

APP_DOMAIN = 'hipeac.net'
ALLOWED_HOSTS = (os.environ.get('DJANGO_ALLOWED_HOST', 'www.hipeac.net'),)
MEDIA_ROOT = '/storage/sites/hipeac/'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True

CRISPY_FAIL_SILENTLY = True


# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

db = urlparse(os.environ.get('DATABASE_URL'))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': db.path[1:],
        'USER': db.username,
        'PASSWORD': db.password,
        'HOST': db.hostname,
        'PORT': db.port,
    }
}


# https://docs.djangoproject.com/en/1.11/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        }
    },
    'staticfiles': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'django-staticfiles',
    },
}

CACHE_MIDDLEWARE_SECONDS = 120
USE_ETAGS = True


# http://celery.readthedocs.org/en/latest/django/

CELERY_BROKER_URL = os.environ.get('RABBITMQ_URL')


# https://docs.djangoproject.com/en/1.11/topics/email/

EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'

DEFAULT_FROM_EMAIL = f'HiPEAC <dev@{APP_DOMAIN}>'
SERVER_EMAIL = f'root@{APP_DOMAIN}'
EMAIL_SUBJECT_PREFIX = f'[{APP_DOMAIN}] '

ANYMAIL = {
    'MAILGUN_API_URL': os.environ.get('MAILGUN_API_URL', 'https://api.eu.mailgun.net/v3'),
    'MAILGUN_API_KEY': os.environ.get('MAILGUN_API_KEY', 'MAILGUN_API_KEY'),
    'MAILGUN_SEND_DEFAULTS': {
        'esp_extra': {
            'sender_domain': os.environ.get('MAILGUN_SENDER_DOMAIN', 'MAILGUN_SENDER_DOMAIN'),
            'o:tag': 'hipeac',
            'o:testmode': 'no',
        }
    }
}


# https://github.com/johnsensible/django-sendfile

SENDFILE_BACKEND = 'sendfile.backends.xsendfile'
SENDFILE_ROOT = '/mnt/hipeac/sites/hipeac/private'
SENDFILE_URL = '/media/private'


# https://docs.djangoproject.com/en/2.1/topics/logging/#django-security
# https://docs.sentry.io/platforms/python/?platform=python

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}
