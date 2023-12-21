from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views import generic

from hipeac.tools.stats.recruitment import get_jobs_per_month

from .inertia import InertiaView


class UserIsSteeringMemberMixin:
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Steering Committee").exists():
            messages.error(request, "You don't have the necessary permissions to view this page.")
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class SteeringCommittee(UserIsSteeringMemberMixin, generic.TemplateView):
    template_name = "steering/steering.html"


class SteeringCommitteeVue(UserIsSteeringMemberMixin, InertiaView):
    vue_entry_point = "apps/steering/main.ts"

    def get_props(self, request, *args, **kwargs):
        return {
            "vue_template": "dark",
            "stats_jobs_per_month": get_jobs_per_month(),
        }
