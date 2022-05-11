from .base import *  # noqa


DEBUG = True

ALLOWED_HOSTS = ("localhost",)
INTERNAL_IPS = ("127.0.0.1",)


# https://django-debug-toolbar.readthedocs.io/en/stable/

try:
    import debug_toolbar  # noqa

    INSTALLED_APPS += ("debug_toolbar",)  # noqa
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)  # noqa
except ModuleNotFoundError:
    pass


# https://docs.djangoproject.com/en/1.11/topics/cache/

CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}


# https://docs.djangoproject.com/en/1.11/topics/email/

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# http://www.django-rest-framework.org/api-guide/settings/

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (  # noqa
    "rest_framework.renderers.JSONRenderer",
    "rest_framework_csv.renderers.CSVRenderer",
    "hipeac.api.renderers.NoFormBrowsableAPIRenderer",
)


# https://github.com/johnsensible/django-sendfile

SENDFILE_BACKEND = "sendfile.backends.development"
