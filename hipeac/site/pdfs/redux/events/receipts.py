from django.template.defaultfilters import date as date_filter
from django.utils import timezone

from hipeac.services.pdf import PdfResponse, Pdf


class ReceiptPdfMaker:
    def __init__(self, *, registration, filename: str, as_attachment: bool = False):
        self._response = PdfResponse(filename=filename, as_attachment=as_attachment)
        self.registration = registration
        self.make_pdf()

    def make_pdf(self):
        reg = self.registration
        event = reg.event
        intro = f"""

{reg.user.profile.name} registered for {event}
on {date_filter(reg.created_at, 'DATE_FORMAT')} and paid {reg.paid} EUR.\u0020\u0020
Payment was done by credit card. Beneficiary of the payment:

_Universiteit Gent_\u0020\u0020
_Sint-Pietersnieuwstraat 25_\u0020\u0020
_BE-9000, Gent_\u0020\u0020
_VAT BE0248015142_
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
            pdf.add_text("Receipt", "h3")
            pdf.add_text(f"ID: {reg.uuid}", "p_small")
            pdf.add_spacer(0.5)
            pdf.add_text("To Whom It May Concern,")
            pdf.add_text(intro, "p", "markdown")
            pdf.add_text(signature, "p", "markdown")
            pdf.add_spacer(1.5)
            pdf.add_text(event.signature, "p", "markdown")
            pdf.add_page_break()

            self._response.write(pdf.get())

    @property
    def response(self) -> PdfResponse:
        return self._response
