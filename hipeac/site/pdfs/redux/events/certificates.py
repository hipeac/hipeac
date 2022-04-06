from django.template.defaultfilters import date as date_filter
from django.utils import timezone

from hipeac.services.pdf import PdfResponse, Pdf


class CertificatePdfMaker:
    def __init__(self, *, registration, filename: str, as_attachment: bool = False):
        self._response = PdfResponse(filename=filename, as_attachment=as_attachment)
        self.registration = registration
        self.make_pdf()

    def make_pdf(self):
        reg = self.registration
        event = reg.event
        where = "virtually" if event.is_virtual else f"in {event.city}, {event.country.name}"
        intro = f"""
On behalf of the {event.name} organizing committee, I would hereby like to confirm that **{reg.user.profile.name}**
— {reg.user.profile.affiliation} — attended {event}
from {date_filter(event.start_date)} to {date_filter(event.end_date)}, {where}.
"""
        signature = f"""
More information about this event can be found on:\u0020\u0020
<{event.website}>

Please do not hesitate to contact me for additional information.\u0020\u0020
Sincerely yours,
"""

        with Pdf() as pdf:
            pdf.add_text(date_filter(timezone.now()), "p_right")
            pdf.add_spacer(1.5)
            pdf.add_text("Certificate of attendance", "h3")
            pdf.add_text(f"ID: {reg.uuid}", "p_small")
            pdf.add_spacer(0.5)
            pdf.add_text("To Whom It May Concern,")
            pdf.add_text(intro, "p", "markdown")

            if reg.sessions.count():
                pdf.add_text(f"{reg.user.profile.name} attended the following sessions:")
                for session in reg.sessions.select_related("track"):
                    if not session.is_social_event:
                        track = f"*{session.track}:* " if session.track else ""
                        t = f'- {track}"{session.title}" ({date_filter(session.date, "N j")})'
                        pdf.add_text(t, "p", "markdown")

            pdf.add_text(signature, "p", "markdown")
            pdf.add_spacer(1.5)
            pdf.add_text(event.signature, "p", "markdown")
            pdf.add_page_break()

            self._response.write(pdf.get())

    @property
    def response(self) -> PdfResponse:
        return self._response
