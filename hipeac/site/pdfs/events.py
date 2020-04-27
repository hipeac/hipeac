from django.template.defaultfilters import date as date_filter

from hipeac.tools.pdf import PdfResponse, Pdf


def get_programme(date):
    return (
        "European Network on High Performance and Embedded Architecture and Compilation",
        "Horizon2020 research and innovation",
        "779656",
    )
    return (
        "European Network on High Performance and Embedded Architecture and Compilation",
        "FP7 ICT Cooperation",
        "779656",
    )


class CertificatePdfMaker:
    def __init__(self, *, registration, filename: str, as_attachment: bool = False):
        self._response = PdfResponse(filename=filename, as_attachment=as_attachment)
        self.registration = registration
        self.make_pdf()

    def make_pdf(self):
        reg = self.registration
        event = reg.event
        programme = get_programme(reg.event.end_date)
        main_text = f"""
On behalf of the {programme[0]} (HiPEAC), funded under the European {programme[1]} programme
under grant agreement number {programme[2]}, I would hereby like to confirm that **{reg.user.profile.name}**
— {reg.user.profile.institution.name} — attended the HiPEAC {event.year} {event.city} {event.type}
from {date_filter(event.start_date)} to {date_filter(event.end_date)} in {event.city}, {event.country.name}.
"""
        signature = f"""
Please do not hesitate to contact me for additional information.<br />
<br />
The coordinator,<br />
<strong>Koen De Bosschere</strong><br />
Ghent University<br />
Gent, Belgium<br />
<a href="mailto:koen.debosschere@ugent.be">koen.debosschere@ugent.be</a>
"""

        with Pdf() as pdf:
            pdf.add_text(str(event), "h4")
            pdf.add_spacer()
            pdf.add_text("Certificate of Attendance", "h1")
            pdf.add_spacer()
            pdf.add_text("To Whom It May Concern,")
            pdf.add_text(main_text, "p", "markdown")
            pdf.add_text(f"{reg.user.profile.name} attended the following sessions:")
            for session in reg.sessions.select_related("session_type"):
                if session.session_type.value != "Social Event":
                    t = f'- *{session.session_type.value}:* "{session.title}"'
                    if session.session_type.value == "Keynote":
                        t = f"{t}, by {session.main_speaker.profile.name} ({session.main_speaker.profile.institution})"
                    pdf.add_text(t, "p", "markdown")
            pdf.add_text(
                f"More information can be found on <https://www.hipeac.net{event.get_absolute_url()}>", "p", "markdown"
            )
            pdf.add_text(signature, "p")
            pdf.add_page_break()

            self._response.write(pdf.get())

    @property
    def response(self) -> PdfResponse:
        return self._response
