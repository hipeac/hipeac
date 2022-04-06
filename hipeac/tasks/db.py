from celery.decorators import periodic_task, task
from celery.schedules import crontab
from django.core.management import call_command
from django.db import connection


@periodic_task(run_every=crontab(hour="*/4", minute=0))
def clear_expired_sessions():
    return call_command("clearsessions")


@periodic_task(run_every=crontab(hour=6, minute=5))
def truncate_notifications_table():
    """This resets table ids and cleans the table."""
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE hipeac_notification")


@task()
def refresh_member_view():
    with connection.cursor() as cursor:
        cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY hipeac_membership_member")
