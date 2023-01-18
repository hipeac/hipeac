import io
import os

from commonmark import Parser
from django.conf import settings
from django.http import HttpResponse
from django.template.defaultfilters import escape
from django.utils import timezone
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Flowable, PageBreak, Paragraph, Image, Spacer
from svglib.svglib import svg2rlg

from .styles import PDF_STYLES, HIPEAC_BLUE


H2020 = (
    "European Union's Horizon Europe research and innovation funding programme under grant agreement number 101069836"
)
DEFAULT_FOOTER = f"""<strong>© {timezone.now().year} HiPEAC</strong>, High Performance, Edge And Cloud computing.<br />The HiPEAC project has received funding from the {H2020}."""


class HeaderNote(Flowable):
    def __init__(self, doc: SimpleDocTemplate, text: str) -> None:
        Flowable.__init__(self)
        self.doc = doc
        self.text = text

    def draw(self) -> None:
        w, h = 7 * cm, 0.7 * cm
        note = Drawing(w, h)
        note.add(Rect(0, 0, w, h, fillColor=HIPEAC_BLUE, strokeColor=None))
        note.add(String(0.5 * cm, 7, self.text, fontName="Roboto-Regular", fontSize=8, fillColor="white"))
        note.drawOn(self.canv, self.doc.width - w - (0.4 * cm), self.doc.topMargin / 2)


class FloatingImage(Flowable):
    def __init__(self, doc: SimpleDocTemplate, image_src: str, size: str = "th") -> None:
        Flowable.__init__(self)
        self.doc = doc
        self.image_src = image_src
        self.size = size

    def draw(self) -> None:
        w, h = 3 * cm, 3 * cm
        image = Image(self.image_src)
        image.drawWidth = w
        image.drawHeight = h
        image.drawOn(self.canv, self.doc.width - w - (0.09 * cm), -(self.doc.topMargin / 1.75))


class MardownParser:
    pass


class Pdf:
    def __init__(self, *args, **kwargs) -> None:
        mt, mr, mb, ml = 3.5 * cm, 2 * cm, 3 * cm, 2 * cm
        self.buffer = io.BytesIO()
        self.parts = []
        self.doc = SimpleDocTemplate(
            self.buffer, pagesize=A4, topMargin=mt, rightMargin=mr, bottomMargin=mb, leftMargin=ml
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.buffer.close()

    def _draw_logo(self, canvas, doc) -> None:
        canvas.saveState()
        drawing = svg2rlg(os.path.join(settings.SITE_ROOT, "static", "images", "hipeac.svg"))
        drawing.drawOn(canvas, doc.leftMargin + (0.2 * cm), doc.height + doc.topMargin + (0.5 * cm))
        canvas.restoreState()

    def _draw_footer(self, canvas, doc) -> None:
        canvas.saveState()
        footer = Paragraph(DEFAULT_FOOTER, PDF_STYLES["footer"])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin + (0.2 * cm), h)
        canvas.restoreState()

    def _first_page(self, canvas, doc) -> None:
        self._draw_logo(canvas, doc)
        self._draw_footer(canvas, doc)

    def _later_pages(self, canvas, doc) -> None:
        self._draw_logo(canvas, doc)
        self._draw_footer(canvas, doc)

    def process_markdown(self, markdown_string: str, paragraph_style: str = "p"):
        walker = Parser().parse(markdown_string).walker()
        event = walker.nxt()
        buf = ""

        while event is not None:
            node, entering = event["node"], event["entering"]
            node_type = node.t
            if node_type == "text":
                buf += node.literal
            if node_type == "softbreak":
                buf += " "
            if node_type == "linebreak":
                buf += "<br />"
            if node_type == "link":
                buf += f'<a href="{escape(node.destination)}">' if entering else "</a>"
            if node_type == "emph":
                buf += "<em>" if entering else "</em>"
            if node_type == "strong":
                buf += "<strong>" if entering else "</strong>"
            if node_type == "paragraph" and not entering:
                style = paragraph_style
                if node.parent.t == "item":
                    style = "ul_li" if node.parent.parent.list_data["type"] == "bullet" else "ol_li"
                self.parts.append(Paragraph(buf, PDF_STYLES[style]))
                buf = ""
            event = walker.nxt()

    def add_note(self, text: str) -> None:
        self.parts.append(HeaderNote(self.doc, text))

    def add_image(self, src: str, size: str = "th") -> None:
        try:
            self.parts.append(FloatingImage(self.doc, src, size))
        except Exception:
            pass

    def add_spacer(self, size_in_cm: float = 0.5) -> None:
        self.parts.append(Spacer(self.doc.width, size_in_cm * cm))

    def add_text(self, text: str, style: str = "p", text_format: str = "regular") -> None:
        if text_format == "markdown":
            try:
                self.process_markdown(text, style)
            except Exception:
                # past-proof: old jobs can even have Word markdown!
                self.parts.append(Paragraph(escape(text), PDF_STYLES[style]))
        else:
            self.parts.append(Paragraph(text, PDF_STYLES[style]))

    def add_page_break(self) -> None:
        self.parts.append(PageBreak())

    def get(self):
        self.doc.build(self.parts, onFirstPage=self._first_page, onLaterPages=self._later_pages)
        return self.buffer.getvalue()


class PdfResponse(HttpResponse):
    def __init__(self, *args, as_attachment: bool = False, filename: str = "", **kwargs):
        self.as_attachment = as_attachment
        self.filename = filename
        kwargs.setdefault("content_type", "application/pdf")
        super().__init__(*args, **kwargs)
