import io

from commonmark import Parser
from django.http import HttpResponse
from django.template.defaultfilters import escape
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, PageBreak, Paragraph, Image, Spacer

from .styles import PDF_STYLES


DEFAULT_FOOTER = f'<strong>© {timezone.now().year} HiPEAC</strong>, ' \
                  'European Network on High Performance and Embedded Architecture and Compilation.<br />' \
                  'The HiPEAC project has received funding from the European Union’s Horizon 2020 ' \
                  'research and innovation programme under grant agreement number 779656.'


class MardownParser:
    pass


class Pdf:

    def __init__(self, *args, **kwargs) -> None:
        mt, mr, mb, ml = 3 * cm, 2 * cm, 3 * cm, 2 * cm
        self.buffer = io.BytesIO()
        self.parts = []
        self.doc = SimpleDocTemplate(self.buffer, pagesize=A4,
                                     topMargin=mt, rightMargin=mr, bottomMargin=mb, leftMargin=ml)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.buffer.close()

    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Header
        header = Paragraph('', PDF_STYLES['footer'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

        # Footer
        footer = Paragraph(DEFAULT_FOOTER, PDF_STYLES['footer'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin + (0.2 * cm), h)

        # Release the canvas
        canvas.restoreState()

    def process_markdown(self, markdown_string: str):
        walker = Parser().parse(markdown_string).walker()
        event = walker.nxt()
        buf = ''

        while event is not None:
            node, entering = event['node'], event['entering']
            node_type = node.t
            if node_type == 'text':
                buf += node.literal
            if node_type == 'softbreak':
                buf += ' '
            if node_type == 'linebreak':
                buf += '<br />'
            if node_type == 'link':
                buf += f'<a href="{escape(node.destination)}">' if entering else '</a>'
            if node_type == 'emph':
                buf += '<em>' if entering else '</em>'
            if node_type == 'strong':
                buf += '<strong>' if entering else '</strong>'
            if node_type == 'paragraph' and not entering:
                style = 'p'
                if node.parent.t == 'item':
                    style = 'ul_li' if node.parent.parent.list_data['type'] == 'bullet' else 'ol_li'
                self.parts.append(Paragraph(buf, PDF_STYLES[style]))
                buf = ''
            event = walker.nxt()

    def add_note(self, text: str) -> None:
        self.parts.append(Paragraph(text, PDF_STYLES['h5']))
        self.add_spacer(1)

    def add_image(self, src: str):
        try:
            self.parts.append(Image(src))
        except Exception:
            pass

    def add_spacer(self, size_in_cm: float = 0.5):
        self.parts.append(Spacer(self.doc.width, size_in_cm * cm))

    def add_text(self, text: str, style: str = 'p'):
        if style == 'markdown':
            try:
                self.process_markdown(text)
            except Exception:
                # past-proof: old jobs can even have Word markdown!
                self.parts.append(Paragraph(escape(text), PDF_STYLES['p']))
        else:
            self.parts.append(Paragraph(text, PDF_STYLES[style]))

    def add_page_break(self):
        self.parts.append(PageBreak())

    def get(self):
        self.doc.build(self.parts, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        return self.buffer.getvalue()


class PdfResponse(HttpResponse):

    def __init__(self, *args, as_attachment: bool = False, filename: str = '', **kwargs):
        self.as_attachment = as_attachment
        self.filename = filename
        kwargs.setdefault('content_type', 'application/pdf')
        super().__init__(*args, **kwargs)
