from django.contrib.messages.views import SuccessMessageMixin
from django.views import generic

from hipeac.models import WebinarProposal
from hipeac.site.forms import WebinarProposalForm

from ..inertia import InertiaView


class WebinarsView(InertiaView):
    page_title = "Webinars"
    vue_entry_point = "apps/webinars/main.ts"


class WebinarProposalView(SuccessMessageMixin, generic.FormView):
    model = WebinarProposal
    form_class = WebinarProposalForm
    template_name = "events/webinars/webinar_proposal.html"


class WebinarProposalCreate(WebinarProposalView, generic.CreateView):
    success_message = "Thank you! We have received your webinar proposal."


class WebinarProposalUpdate(WebinarProposalView, generic.UpdateView):
    success_message = "Thank you! Your webinar proposal has been updated."

    def get_object(self, queryset=None):
        return WebinarProposal.objects.get(uuid=self.kwargs.get("slug"))
