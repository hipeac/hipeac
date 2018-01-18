from django.conf.urls import include
from django.urls import re_path
from rest_framework.documentation import include_docs_urls

from .routers import Router


urlpatterns = [
    re_path(r'^v1/', include((Router('v1').urls, 'api'), namespace='v1')),
    re_path(r'^', include_docs_urls(title='HiPEAC API')),
]
