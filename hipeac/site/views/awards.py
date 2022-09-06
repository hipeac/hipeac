from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic

from hipeac.models import Member, TechTransferCall, TechTransferApplication
from hipeac.site.forms import TechTransferApplicationForm


class TechTransferApplicationFormView(generic.FormView):
    model = TechTransferApplication
    form_class = TechTransferApplicationForm
    template_name = "awards/tech_transfer_application.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not Member.objects.filter(user=request.user).exists():
            messages.error(
                self.request,
                "Sorry but only HiPEAC Members, Affiliate Members or "
                "Affiliate PHD Students (as part of the academic team) can currently apply "
                "for a Technology Transfer Award.",
            )
            raise PermissionDenied
        try:
            today = timezone.now().date()
            self.call = TechTransferCall.objects.get(start_date__lte=today, end_date__gte=today)
        except TechTransferCall.DoesNotExist:
            messages.error(self.request, "There is currently no Tech Transfer Call open.")
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["call"] = self.call
        return context


class TechTransferApplicationCreateView(TechTransferApplicationFormView, generic.edit.CreateView):
    success_message = "Thank you! We have received your tech transfer application."

    def get_initial(self):
        return {
            "call": self.call,
            "applicant": self.request.user,
        }


class TechTransferApplicationUpdateView(TechTransferApplicationFormView, generic.edit.UpdateView):
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.applicant.id != self.request.user.id:
            messages.error(
                self.request,
                "Sorry but you don't have the necessary permissions " "to update this Technology Transfer application.",
            )
            raise PermissionDenied
        return obj
