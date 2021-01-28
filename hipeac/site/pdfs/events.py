from django.template.defaultfilters import date as date_filter

from hipeac.tools.pdf import PdfResponse, Pdf
from hipeac.tools.zoom import attendee_report


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

        if registration.is_paid:
            self.make_pdf()
        else:
            self.not_paid()

    def make_pdf(self):
        reg = self.registration
        event = reg.event
        inst = reg.user.profile.institution
        institution = "— {inst.name} — " if inst else ""
        location = "virtual event" if event.is_virtual else f"event in {event.city}, {event.country.name}"
        programme = get_programme(event.end_date)
        main_text = f"""
On behalf of the {programme[0]} (HiPEAC), funded under the European {programme[1]} programme
under grant agreement number {programme[2]}, I would hereby like to confirm that **{reg.user.profile.name}**
{institution}attended the <strong>{event}</strong> {location},
from {date_filter(event.start_date)} to {date_filter(event.end_date)}.
"""
        signature = """
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

    def not_paid(self):
        reg = self.registration
        event = reg.event
        main_text = """
**Not available.**<br />
Contact us if you think this is a mistake: <management@hipeac.net>
"""
        with Pdf() as pdf:
            pdf.add_text(str(event), "h4")
            pdf.add_spacer()
            pdf.add_text("Certificate of Attendance", "h1")
            pdf.add_spacer()
            pdf.add_text(main_text, "p", "markdown")
            pdf.add_page_break()

            self._response.write(pdf.get())

    @property
    def response(self) -> PdfResponse:
        return self._response


class VirtualEventCertificatePdfMaker:
    def __init__(self, *, registration, filename: str, as_attachment: bool = False):
        self._response = PdfResponse(filename=filename, as_attachment=as_attachment)
        self.registration = registration
        self.make_pdf()

    def make_pdf(self):
        reg = self.registration
        event = reg.event
        u = reg.user
        emails = [u.email] + [e.email for e in u.emailaddress_set.all()]
        courses_completed = []

        programme = get_programme(reg.event.end_date)
        event_name = (
            f"HiPEAC {event.year} {event.city} {event.type}" if event.type == "ACACES" else "ACACES Summer School"
        )
        main_text = f"""
On behalf of the {programme[0]} (HiPEAC), funded under the European {programme[1]} programme
under grant agreement number {programme[2]}, I would hereby like to confirm that **{reg.user.profile.name}**
— {reg.user.profile.institution.name} — attended the virtual {event_name}
from {date_filter(event.start_date)} to {date_filter(event.end_date)}.
"""
        signature = """
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
            pdf.add_text(f"{reg.user.profile.name} attended all sessions for the following courses:")

            for course in reg.courses.all():
                attended = set()

                for session in course.sessions.all():
                    if session.zoom_attendee_report:
                        sminutes, report = attendee_report(str(session.zoom_attendee_report.file))
                        uminutes = 0

                        for r in report:
                            if r["attended"] and r["email"] in emails:
                                uminutes += r["minutes"]

                        if uminutes > 0:
                            attended.add((uminutes / sminutes) >= 0.5)

                if len(attended) > 0 and False not in attended:
                    t = f'- *{course.teachers_string}:* "{course.title}" ({course.hours} h)'
                    courses_completed.append(t)

            courses_completed.sort()
            for c in courses_completed:
                pdf.add_text(c, "p", "markdown")

            posters_count = reg.posters.count()

            if posters_count > 0:
                s = "s" if posters_count > 1 else ""
                pdf.add_text(f"and presented the following poster{s} in the Poster Session:")
                for poster in reg.posters.all():
                    pdf.add_text(f'- "{poster.title}", _{poster.authors}_', "p", "markdown")

            pdf.add_text(
                f"More information can be found on <https://www.hipeac.net{event.get_absolute_url()}>", "p", "markdown"
            )
            pdf.add_text(signature, "p")
            pdf.add_page_break()

            pdf_response = pdf.get()

        if len(courses_completed) == 0:
            self.no_pdf()
            return

        self._response.write(pdf_response)

    def no_pdf(self):
        reg = self.registration
        event = reg.event
        main_text = """
**Not available.**<br />
Contact us if you think this is a mistake: <management@hipeac.net>
"""

        with Pdf() as pdf:
            pdf.add_text(str(event), "h4")
            pdf.add_spacer()
            pdf.add_text("Certificate of Attendance", "h1")
            pdf.add_spacer()
            pdf.add_text(main_text, "p", "markdown")
            pdf.add_page_break()

            self._response.write(pdf.get())

    @property
    def response(self) -> PdfResponse:
        return self._response
