from django.conf.urls import include
from django.urls import re_path
from rest_framework.documentation import include_docs_urls

from .routers import Router
from .views import ContactUser


urlpatterns = [
    re_path(r"^contact/", ContactUser.as_view()),
    re_path(r"^v1/", include((Router("v1").urls, "api"), namespace="v1")),
    re_path(
        r"^",
        include_docs_urls(
            title="HiPEAC API", description="Add `?format=csv` to the request URL if you want to download a CSV file.",
        ),
    ),
]
