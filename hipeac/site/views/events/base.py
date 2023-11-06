from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import date as date_filter
from django.utils.decorators import method_decorator
from django.views import generic

from hipeac.models import Dissemination, Event, Registration, SessionProposal
from hipeac.services.pdf import H2020, Pdf, PdfResponse
from hipeac.site.forms import SessionProposalForm, ThematicSessionProposalForm
from hipeac.site.views.mixins import SlugMixin


class EventDetail(generic.DetailView):
    """
    Displays a Event page.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """

    model = Event
    template_name = "events/event/event.html"

    def get_object(self, queryset=None):
        if not hasattr(self, "object"):
            self.object = self.get_queryset().get(
                start_date__year=self.kwargs.get("year"),
                slug=self.kwargs.get("slug"),
            )
        return self.object


class EventB2BDetail(SlugMixin, generic.DetailView):
    """
    Displays a Event B2B page.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """

    model = Event
    template_name = "events/event/b2b.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not hasattr(self, "object"):
            self.object = self.get_queryset().get(
                type="conference", start_date__year=self.kwargs.get("year"), slug=self.kwargs.get("slug")
            )
        return self.object


class RoadshowDetail(SlugMixin, generic.DetailView):
    """
    Displays a Roadshow.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """

    model = Dissemination
    template_name = "events/roadshow/roadshow.html"

    def get_queryset(self):
        return super().get_queryset().filter(type="roadshow").prefetch_related("rel_institutions__institution")

    def get_object(self, queryset=None):
        if not hasattr(self, "object"):
            self.object = self.get_queryset().get(id=self.kwargs.get("pk"))
        return self.object


class RegistrationReceiptPdfView(generic.DetailView):
    model = Registration
    queryset = Registration.objects.select_related("event", "user__profile")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Checks if the user has necessary privileges.
        """
        if not self.get_object().is_paid:
            messages.error(request, "Receipt can only be viewed once the registration has been paid.")
            raise PermissionDenied
        if not request.user.is_staff and self.get_object().user.id != request.user.id:
            messages.error(request, "You don't have the necessary permissions to view this file.")
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        registration = self.get_object()
        maker = JobsPdfMaker(registration=registration, filename=f"hipeac--{registration.id}.pdf", as_attachment=False)
        return maker.response


class JobsPdfMaker:
    def __init__(self, *, registration, filename: str, as_attachment: bool = False):
        self._response = PdfResponse(filename=filename, as_attachment=as_attachment)
        self.registration = registration
        self.make_pdf()

    def make_pdf(self):
        with Pdf() as pdf:
            reg = self.registration
            attended = "attended" if reg.event.is_finished() else "will attend"
            institution = f" —{reg.user.profile.institution.name}—" if reg.user.profile.institution else ""
            location = "virtual event" if reg.event.is_virtual else f"event in {reg.event.country.name}"

            pdf.add_text(str(reg.event), "h4")
            pdf.add_text(f"Receipt (#{reg.id})", "h1")
            pdf.add_text("To Whom It May Concern,", "p")
            pdf.add_text(
                f"""On behalf of the European Network on High-performance Embedded Architecture and
Compilation (HiPEAC), funded under the {H2020}, I would hereby like to confirm that <strong>{reg.user.profile.name}
{institution}</strong> {attended} the <strong>{reg.event}</strong> {location}, between
{date_filter(reg.event.start_date)} and {date_filter(reg.event.end_date)}.""",
                "p",
            )
            pdf.add_text(
                f"""{reg.user.profile.name} registered for this event on {date_filter(reg.created_at)} and
paid the registration fee of <strong>EUR {reg.total_fee}</strong>.""",
                "p",
            )
            pdf.add_text(
                f"""More information about {reg.event} can be found on
<strong>hipeac.net{reg.event.get_absolute_url()}</strong>.""",
                "p",
            )
            pdf.add_text("Please do not hesitate to contact me for additional information.", "p")
            pdf.add_text("The coordinator,<br/>Koen De Bosschere", "p")
            pdf.add_page_break()

            self._response.write(pdf.get())

    @property
    def response(self) -> PdfResponse:
        return self._response


class SessionProposalView(SuccessMessageMixin, generic.FormView):
    model = SessionProposal
    template_name = "events/event/session_proposal.html"

    def dispatch(self, request, *args, **kwargs):
        event = self.get_event()

        # if event.is_ready:
        #    return redirect(event.get_absolute_url())

        if event.type not in [Event.CONFERENCE, Event.CSW]:
            messages.error(request, "You cannot submit a proposal for this event.")
            raise PermissionDenied

        if event.is_finished():
            messages.error(request, "You cannot submit a proposal for a past event.")
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        if self.get_event().type == Event.CSW:
            return ThematicSessionProposalForm
        return SessionProposalForm

    def get_event(self, **kwargs):
        if not hasattr(self, "event"):
            self.event = Event.objects.get(pk=self.kwargs.get("pk"))
        return self.event

    def get_context_data(self, **kwargs):
        event = self.get_event()
        context = super().get_context_data()
        context["event"] = event
        context["subtitle"] = "Thematic Sessions" if event.type == Event.CSW else "workshop and tutorials"
        context["intro"] = (
            (
                "Please fill in all the information relative to your Thematic Session proposal "
                "and submit it for review."
            )
            if event.type == Event.CSW
            else (
                "In parallel with the main paper track, a number of workshops and tutorials will be held. "
                "To submit your workshop or tutorial proposal, please complete the following form."
            )
        )
        return context


class SessionProposalCreate(SessionProposalView, generic.CreateView):
    success_message = "Thank you! We have received your session proposal."

    def get_initial(self):
        return {"event": self.get_event()}


class SessionProposalUpdate(SessionProposalView, generic.UpdateView):
    success_message = "Thank you! Your session proposal has been updated."

    def get_object(self, queryset=None):
        return SessionProposal.objects.get(uuid=self.kwargs.get("slug"))
