from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path


admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("hipeac.api.urls")),
    path("", include("hipeac.site.urls")),
]

if settings.DEBUG:
    try:
        import debug_toolbar  # noqa
        from django.contrib.staticfiles.urls import staticfiles_urlpatterns

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
        urlpatterns += staticfiles_urlpatterns()
    except ModuleNotFoundError:
        pass


# error handlers

handler403 = "hipeac.site.views.errors.permission_denied_error"
handler500 = "hipeac.site.views.errors.server_error"
