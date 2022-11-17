from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic

from hipeac.models import Event, Profile, Registration
from hipeac.site.pdfs.events import CertificatePdfMaker, VirtualEventCertificatePdfMaker


class UserProfile(generic.DetailView):
    """
    Displays a User profile.
    """

    queryset = Profile.objects.public()
    context_object_name = "profile"
    slug_field = "user__username"
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["phd_mobilities"] = self.get_object().user.phd_mobilities.select_related("institution")
        return context


class UserAuthenticatedMixin:
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class UserSettings(UserAuthenticatedMixin, generic.TemplateView):
    template_name = "__v3__/users/user/settings.html"


class UserCertificates(UserAuthenticatedMixin, generic.ListView):
    template_name = "users/user/certificates.html"

    def get_queryset(self):
        today = timezone.now().date()
        return self.request.user.registration_registrations.filter(event__end_date__lte=today).select_related("event")


class UserCertificatePdf(UserAuthenticatedMixin, generic.DetailView):
    model = Registration

    def get_object(self):
        if not hasattr(self, "object"):
            self.object = (
                self.request.user.registration_registrations.select_related("user__profile")
                .prefetch_related("user__profile__institution")
                .get(uuid=self.kwargs.get("uuid"))
            )
        return self.object

    def get(self, request, *args, **kwargs):
        reg = self.get_object()
        check_zoom = reg.event.is_virtual and reg.event.type == "ACACES"
        PdfMaker = VirtualEventCertificatePdfMaker if check_zoom else CertificatePdfMaker
        maker = PdfMaker(registration=reg, filename=f"hipeac-certificate--{reg.id}.pdf", as_attachment=False)
        return maker.response
