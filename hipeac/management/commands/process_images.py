from celery.execute import send_task
from django.core.management.base import BaseCommand

from hipeac.models import Institution, Project


class Command(BaseCommand):
    help = 'Processes images and saves new images.'

    def handle(self, *args, **options):
        for institution in Institution.objects.all():
            if institution.image:
                send_task('hipeac.tasks.imaging.generate_image_variants', (institution.image.path,))

        for project in Project.objects.all():
            if project.image:
                send_task('hipeac.tasks.imaging.generate_image_variants', (project.image.path,))
