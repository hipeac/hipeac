from hipeac.tools.pdf import PdfResponse, Pdf


class TechTransferCallPdfMaker:
    def __init__(self, *, calls, filename: str, as_attachment: bool = False):
        self._response = PdfResponse(filename=filename, as_attachment=as_attachment)
        self.calls = calls
        self.make_pdf()

    def make_pdf(self):
        with Pdf() as pdf:
            for call in self.calls:
                pdf.add_spacer(4)
                pdf.add_text(f"<strong>Call: {str(call).upper()}</strong>", "h1")
                pdf.add_spacer()
                pdf.add_page_break()

                for ap in call.applications.all():
                    pdf.add_text("<small>Tech Transfer application</small>", "p")
                    pdf.add_text(f"#{ap.id}: {ap.title}", "h1")
                    pdf.add_text(f"<strong>Applicant</strong>: {ap.applicant.profile.name}", "ul_li")
                    pdf.add_text(f"<strong>Affiliation</strong>: {ap.applicant.profile.institution}", "ul_li")
                    pdf.add_text(f"<strong>Email</strong>: {ap.applicant.email}", "ul_li")
                    pdf.add_spacer()
                    pdf.add_text("Description of the technology being transferred", "h4")
                    pdf.add_text(ap.description, "p_justify", "markdown")
                    pdf.add_spacer()
                    pdf.add_text("Description of the academic partners and the company involved", "h4")
                    pdf.add_text(ap.partners_description, "p_justify", "markdown")
                    pdf.add_spacer()
                    pdf.add_text("Estimate of the value of the agreement", "h4")
                    pdf.add_text(ap.value, "p_justify", "markdown")
                    pdf.add_page_break()

            self._response.write(pdf.get())

    @property
    def response(self) -> PdfResponse:
        return self._response
