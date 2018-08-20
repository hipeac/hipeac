import os

from urllib.parse import urlparse

from .base import *  # noqa


DEBUG = False

APP_DOMAIN = 'hipeac.net'
ALLOWED_HOSTS = ('v5.{0}'.format(APP_DOMAIN),)
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

DEFAULT_FROM_EMAIL = 'HiPEAC <dev@{0}>'.format(APP_DOMAIN)
SERVER_EMAIL = 'root@{0}'.format(APP_DOMAIN)
EMAIL_SUBJECT_PREFIX = '[{0}] '.format(APP_DOMAIN)

ANYMAIL = {
    'MAILGUN_API_URL': os.environ.get('MAILGUN_API_URL', 'https://api.mailgun.net/v3'),
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


# https://docs.djangoproject.com/en/1.11/topics/logging/#django-security
# https://docs.sentry.io/clients/python/integrations/django/

INSTALLED_APPS += ['raven.contrib.django.raven_compat']  # noqa

RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_DSN', 'SENTRY_DSN'),
    'release': os.environ.get('GIT_REV', None),
    'IGNORE_EXCEPTIONS': ['django.security.DisallowedHost'],
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
