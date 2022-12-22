import os

from urllib.parse import urlparse

from .base import *  # noqa


DEBUG = True
TEST = True

ALLOWED_HOSTS = ("localhost",)
INTERNAL_IPS = ("127.0.0.1",)


# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

if os.environ.get("GITHUB_WORKFLOW"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "github_actions",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "127.0.0.1",
            "PORT": "5432",
        }
    }
else:
    db = urlparse(os.environ.get("TEST_DATABASE_URL"))
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": db.path[1:],
            "USER": db.username,
            "PASSWORD": db.password,
            "HOST": db.hostname,
            "PORT": db.port,
        },
    }


# https://docs.djangoproject.com/en/1.11/topics/cache/

CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}


# https://docs.djangoproject.com/en/1.11/topics/email/

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# https://django-compressor.readthedocs.io/en/stable/settings/

COMPRESS_ENABLED = False
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
