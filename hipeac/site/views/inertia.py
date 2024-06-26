import os

from django.conf import settings
from django.middleware.csrf import get_token as get_csrf_token
from django.urls import reverse
from django.utils.text import slugify
from django.views.generic import View
from inertia import render

from hipeac.templatetags.hipeac import active


def get_site_menu(request):
    return [
        ("Network", reverse("network"), active(request, "network,user,institution,project")),
        ("Events", reverse("events"), active(request, "events,acaces,conference,conference_v2,csw,roadshow")),
        ("Webinars", reverse("webinars"), active(request, "webinars")),
        ("Jobs", reverse("jobs"), active(request, "jobs,job")),
        ("Vision", reverse("vision"), active(request, "vision")),
        ("Awards", reverse("awards"), active(request, "awards")),
        ("TV", "/tv/", ""),
        ("News", reverse("news"), active(request, "news,article")),
        ("Press room", reverse("press"), active(request, "press")),
    ]


def render_inertia(request, vue_entry_point: str, *, props: dict | None, page_title: str | None = None):
    """
    Render a Vue component with Inertia.
    It adds some basic props that can be helpful.
    """

    return render(
        request,
        slugify(vue_entry_point),
        props={
            "django_csrf_token": get_csrf_token(request),
            "django_debug": settings.DEBUG,
            "django_user": request.user if request.user.is_authenticated else None,
            "git_commit_hash": os.environ.get("GIT_REV", "None"),
            "site_menu": get_site_menu(request),
            "vue_template": "light",
        }
        | (props or {}),
        template_data={
            "page_title": page_title or "HiPEAC",
            "vue_entry_point": vue_entry_point,
        },
    )


class InertiaView(View):
    page_title: str | None = None
    vue_entry_point: str

    def get_page_title(self, request, *args, **kwargs) -> str | None:
        return f"{self.page_title} - HiPEAC" if self.page_title and self.page_title != "HiPEAC" else None

    def get_props(self, request, *args, **kwargs) -> dict:
        return {}

    def get(self, request, *args, **kwargs):
        if not self.vue_entry_point:
            raise NotImplementedError("`vue_entry_point` must be set")

        return render_inertia(
            request,
            self.vue_entry_point,
            props=self.get_props(request, *args, **kwargs),
            page_title=self.get_page_title(self, request, *args, **kwargs),
        )
