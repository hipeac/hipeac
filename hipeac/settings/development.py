from .base import *  # noqa


DEBUG = True

ALLOWED_HOSTS = ('localhost',)
INTERNAL_IPS = ('127.0.0.1',)


# https://django-debug-toolbar.readthedocs.io/en/stable/

try:
    import debug_toolbar  # noqa
    INSTALLED_APPS += ('debug_toolbar',)  # noqa
    MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)  # noqa
except Exception as e:
    pass


# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hipeac_dev',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
}


# https://docs.djangoproject.com/en/1.11/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
        'TIMEOUT': 0,
    }
}


# https://docs.djangoproject.com/en/1.11/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# https://github.com/johnsensible/django-sendfile

SENDFILE_BACKEND = 'sendfile.backends.development'
