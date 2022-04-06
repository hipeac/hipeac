from django.core.management import call_command
from huey import crontab
from huey.contrib.djhuey import db_periodic_task


@db_periodic_task(crontab(hour="*/4", minute=0))
def clear_expired_sessions():
    return call_command("clearsessions")
