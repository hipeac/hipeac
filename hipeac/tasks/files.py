from celery.decorators import periodic_task
from celery.schedules import crontab
from django.utils import timezone

from hipeac.models.files import File


@periodic_task(run_every=crontab(hour="*/4", minute=0))
def remove_old_cvs():
    four_months_ago = timezone.now().date() - timezone.timedelta(days=120)

    for file in File.objects.filter(keywords__contains=["cv"], created_at__lt=four_months_ago):
        file.delete()

    return
