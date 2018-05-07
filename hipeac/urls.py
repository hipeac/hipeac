from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import re_path


admin.autodiscover()

urlpatterns = [
    # API
    re_path(r'^api/', include('hipeac.api.urls')),
    # Admin
    re_path(r'^accounts/', include('allauth.urls')),
    re_path(r'^admin/', admin.site.urls),
    # HiPEAC
    re_path(r'^', include('hipeac.site.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
