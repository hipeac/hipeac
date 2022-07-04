from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter, PageObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from hipeac.models.events.acaces import AcacesPoster
from hipeac.services.pdf import PdfResponse


def merge_abstract_pdfs(acaces, *, filename: str, as_attachment: bool = False) -> PdfResponse:
    response = PdfResponse(filename=filename, as_attachment=as_attachment)
    writer = PdfWriter()

    i = 0

    def get_header(year: str, num: int) -> PdfReader:
        b = BytesIO()
        c = canvas.Canvas(b, pagesize=A4)
        c.setFontSize(8)
        c.drawCentredString(A4[0] / 2, A4[1] - 40, f"ACACES {year} - Poster Abstracts")
        if num % 2 == 0:
            c.drawString(45, A4[1] - 40, str(num))
        else:
            c.drawRightString(A4[0] - 45, A4[1] - 40, str(num))
        c.save()
        b.seek(0)
        return PdfReader(b)

    for poster in AcacesPoster.objects.filter(
        position__gt=0, registration__event_id=acaces.id, registration__accepted=True
    ).order_by("position"):
        if poster.abstract:
            pdf_file = open(poster.abstract.path, "rb")
            pdf_reader = PdfReader(pdf_file)
            for page in pdf_reader.pages:
                i += 1
                page.scale_to(width=8.268 * 72, height=11.693 * 72)
                page.merge_page(get_header(acaces.year, i).pages[0], True)
                writer.add_page(page)
            if len(pdf_reader.pages) % 2 == 1:
                i += 1
                blank_page = PageObject.create_blank_page(pdf_reader)
                blank_page.merge_page(get_header(acaces.year, i).pages[0], True)
                writer.add_page(blank_page)

    with BytesIO() as bytes_stream:
        writer.remove_links()
        writer.write(bytes_stream)
        response.write(bytes_stream.getvalue())

    return response
