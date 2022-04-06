import os

from django.conf import settings
from django.template.defaultfilters import date as date_filter
from reportlab.graphics.shapes import Drawing, Image, Rect, String
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm

from hipeac.models.metadata import Metadata
from hipeac.services.pdf import PdfResponse
from hipeac.services.pdf.styles import HIPEAC_BLUE
from hipeac.services.pdf.wrapdf import Wrapdf


def get_font_size(text, *, max_size: float, char_max: int) -> float:
    """Return a text size based on the length of the text."""
    if len(text) <= char_max:
        return max_size
    return max_size / (len(text) / char_max)


class BadgesPdfMaker:
    def __init__(self, *, registrations, filename: str, as_attachment: bool = True):
        self._response = PdfResponse(filename=filename, as_attachment=as_attachment)
        self.registrations = registrations.select_related("event", "user__profile__institution").order_by(
            "user__first_name", "user__last_name"
        )
        self.make_pdf()

    def make_pdf(self):
        side_margin = 6 * mm  # a minimum on the sides for the printers
        width = (210 * mm) - (2 * side_margin)
        height = 85 * mm
        hipeac_blue = HexColor(HIPEAC_BLUE)
        logo_path = os.path.join(settings.SITE_ROOT, "static", "images", "hipeac--avatar.png")
        social_event = Metadata.objects.get(type=Metadata.SESSION_TYPE, value="Social Event")

        with Wrapdf(margins=[10 * mm, 0, 10 * mm, side_margin]) as pdf:
            i = 0

            for reg in self.registrations:
                i += 1
                event_name = f"HiPEAC {reg.event.name}" if reg.event.type == "csw" else reg.event.name
                event_info = (
                    f"{date_filter(reg.event.start_date, ('F j'))}-{date_filter(reg.event.end_date, ('j'))}, "
                    f"{reg.event.city}, {reg.event.country.name}"
                )
                institution = reg.user.profile.institution.name if reg.user.profile.institution else ""
                country = reg.user.profile.institution.country.name if reg.user.profile.institution else ""

                draw = Drawing(width, height)
                draw.add(Rect(0, 0, width, 10 * mm, fillColor=hipeac_blue, strokeColor=hipeac_blue))
                draw.add(Rect(0, 10 * mm, width, 63 * mm, fillColor="white", strokeColor="white"))
                draw.add(Rect(0, 73 * mm, width, 10 * mm, fillColor="black", strokeColor="black"))
                draw.add(Rect(0, 83 * mm, width, 2 * mm, fillColor="white", strokeColor="white"))

                for x, text in [(width * 0.25, event_name), (width * 0.75, f"#{reg.event.hashtag}")]:
                    draw.add(
                        String(
                            x,
                            height - (8.5 * mm),
                            text,
                            fontName="Roboto Light",
                            fillColor="white",
                            fontSize=13,
                            textAnchor="middle",
                        )
                    )

                for x in [width * 0.25, width * 0.75]:
                    image_width = 15 * mm
                    draw.add(Image(x - (image_width / 2), 12 * mm, image_width, image_width, logo_path))

                    draw.add(
                        String(
                            x,
                            55 * mm,
                            reg.user.profile.name,
                            fontName="Roboto Medium",
                            fillColor="black",
                            fontSize=get_font_size(reg.user.profile.name, max_size=26.0, char_max=17),
                            textAnchor="middle",
                        )
                    )

                    draw.add(
                        String(
                            x,
                            43 * mm,
                            institution,
                            fontName="Roboto Light",
                            fillColor="black",
                            fontSize=get_font_size(institution, max_size=14.0, char_max=36),
                            textAnchor="middle",
                        )
                    )

                    draw.add(
                        String(
                            x,
                            37 * mm,
                            country,
                            fontName="Roboto Light",
                            fillColor="black",
                            fontSize=get_font_size(country, max_size=11.0, char_max=50),
                            textAnchor="middle",
                        )
                    )

                    draw.add(
                        String(
                            x,
                            3 * mm,
                            event_info,
                            fontName="Roboto Light",
                            fillColor="white",
                            fontSize=13,
                            textAnchor="middle",
                        )
                    )

                if reg.sessions.filter(type=social_event).exists():
                    draw.add(
                        String(
                            width / 2,
                            -6 * mm,
                            "*",
                            fontName="Roboto Bold",
                            fillColor="white",
                            fontSize=66,
                            textAnchor="middle",
                        )
                    )

                pdf.parts.append(draw)

                if i % 3 == 0:
                    pdf.add_page_break()

            self._response.write(pdf.get())

    @property
    def response(self) -> PdfResponse:
        return self._response
