from django.core.management.base import BaseCommand

from hipeac.functions import send_task
from hipeac.models import Event


class Command(BaseCommand):
    help = 'Processes images and saves new images.'

    def handle(self, *args, **options):
        for event in Event.objects.all():
            if event.image:
                send_task('hipeac.tasks.imaging.generate_banner_variants', (event.image.path,))
