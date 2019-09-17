from celery.decorators import periodic_task
from celery.schedules import crontab

from hipeac.tools.notifications.events import RegistrationPendingNotificator


@periodic_task(run_every=crontab(minute='5,15,25,35,45,55'))
def process_registration_notifications():
    RegistrationPendingNotificator().process_data()
