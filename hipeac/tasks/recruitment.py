from celery.decorators import periodic_task
from celery.task.schedules import crontab
from datetime import timedelta
from django.core.mail import send_mail
from django.utils import timezone

from hipeac.models import Job


RECRUITMENT_EMAIL = 'recruitment@hipeac.net'


@periodic_task(run_every=crontab(day_of_week='mon-fri', hour=10, minute=0), max_retries=3)
def send_expiration_reminders():
    """Sends an email when a Job is about to expire."""
    send_mail(
        '[HiPEAC Bot] Job expiration reminders sent (10h)',
        'N reminders have been sent to: company1, company2.',
        'noreply@hipeac.net',
        ['eneko@illarra.com'],
        fail_silently=True,
    )


@periodic_task(run_every=crontab(day_of_week='mon-fri', hour=10, minute=0), max_retries=3)
def send_evaluations():
    two_weeks_ago = (timezone.now() - timedelta(days=14)).date()
    jobs = Job.objects.filter(deadline__lte=two_weeks_ago)
    send_mail(
        '[HiPEAC Bot] Job evaluations sent (10h10)',
        'N evalution emails have been sent to: company1, company2.',
        'noreply@hipeac.net',
        ['eneko@illarra.com'],
        fail_silently=True,
    )


@periodic_task(run_every=crontab(day_of_week='fri', hour=10, minute=0), max_retries=3)
def send_weekly_digest():
    """Sends a digest to publicity@hipeac.net with the Jobs posted in the last 2 weeks, every two weeks."""
    today = timezone.now().date()
    week_number = int(today.strftime('%U'))
    if week_number % 2 == 0:  # ignore even weeks; @periodic_task doesn't allow this
        return

    send_mail(
        'Latest computing jobs and opportunities (10h)',
        'Includes jobs posted in the last two weeks.',
        'noreply@hipeac.net',
        ['eneko@illarra.com'],
        fail_silently=True,
    )


"""
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from celery.utils.log import get_task_logger
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from twitter import *

from .emails import send_job_reminder, send_job_evaluation
from .models import Job

logger = get_task_logger(__name__)


@periodic_task(run_every=crontab(hour='9', minute='0', day_of_week='mon-fri'))
def send_expiration_reminders():
    today = timezone.now().date()
    in_five_days = (timezone.now() + timedelta(days=5)).date()
    jobs = Job.objects.filter(deadline__gte=today, deadline__lte=in_five_days)

    for job in jobs:
        if job.share and not job.reminder_sent_for and not settings.DEBUG:
            oauth_twitter = settings.OAUTH_TWITTER
            t = Twitter(auth=OAuth(oauth_twitter['access_token'], oauth_twitter['access_token_secret'],
                                   oauth_twitter['api_key'], oauth_twitter['api_secret']))
            t.statuses.update(status=job.get_status(True, True, True, 'Last days to apply to '))

    sent = send_job_reminder(jobs)

    if sent:
        logger.info('Job reminders sent.')
    else:
        logger.warning('No job reminders have been sent.')


@periodic_task(run_every=crontab(hour='9', minute='0', day_of_week='mon-fri'))
def send_evaluations():
    two_weeks_ago = (timezone.now() - timedelta(days=14)).date()
    jobs = Job.objects.filter(deadline__lte=two_weeks_ago)
    sent = send_job_reminder(jobs)

    if sent:
        logger.info('Job evaluations sent.')
    else:
        logger.warning('No job evaluations have been sent.')
"""
