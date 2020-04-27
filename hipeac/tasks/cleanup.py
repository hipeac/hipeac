from celery.decorators import periodic_task
from celery.schedules import crontab
from django.db import connection


@periodic_task(run_every=crontab(hour=6, minute=5))
def truncate_notifications_table():
    """ This resets table ids and cleans the table.
    """
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE hipeac_notification")
