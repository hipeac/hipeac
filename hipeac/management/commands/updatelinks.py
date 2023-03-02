import requests
import time

from django.core.management.base import BaseCommand

from hipeac.models import Link


class Command(BaseCommand):
    """Check URLs and update them if they have changed, e.g. due to redirects."""

    def add_arguments(self, parser):
        parser.add_argument("--type", type=str, help="Filter links by type.")

    def handle(self, *args, **kwargs):
        if kwargs["type"]:
            links = Link.objects.filter(type=kwargs["type"]).all()
        else:
            links = Link.objects.all()

        for link in links:
            """Wait 200 ms between requests to avoid overloading the servers."""
            time.sleep(0.2)

            try:
                r = requests.get(link.url)

                if r.status_code == 404:
                    link.delete()
                    print(f"Deleted link: {link.url}")
                    continue

                if link.url != r.url:
                    link.url = r.url
                    link.save()
                    print(f"Updated link: {r.url}")

            except requests.exceptions.RequestException:
                pass
