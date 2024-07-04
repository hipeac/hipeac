from django.core.management.base import BaseCommand

from hipeac.models import WebinarRegistration
from hipeac.services.zoom import Zoomer


class Command(BaseCommand):
    """Update registration links for a Zoom webinar."""

    def handle(self, *args, **kwargs):
        for registration in WebinarRegistration.objects.filter(zoom_access_link__contains="'code':").all():
            if registration.webinar.zoom_webinar_int:
                user_data = {
                    "email": registration.user.email,
                    "first_name": registration.user.first_name,
                    "last_name": registration.user.last_name,
                    "country": registration.user.profile.country.code if registration.user.profile.country else None,
                }
                access_link = Zoomer().post_webinar_registrant(registration.webinar.zoom_webinar_int, user_data)

                try:
                    registration.zoom_access_link = access_link
                    registration.save()
                    print(f"Updated registration link: {access_link}")
                except Exception as e:
                    print(f"Failed to update registration link: {e}")
