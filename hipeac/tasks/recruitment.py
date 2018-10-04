import datetime
import json

from celery.decorators import periodic_task, task
from celery.task.schedules import crontab
from datetime import timedelta
from django.core.mail import send_mail
from django.db.models import Q, F
from django.utils import timezone
from typing import Optional, Tuple

from hipeac.models import Job
from hipeac.tools.language import NaturalLanguageAnalyzer
from hipeac.tools.linkedin import LinkedInManager
from hipeac.tools.twitter import Tweeter


JOBS_DIGEST_EMAIL = 'jobs@hipeac.net'
RECRUITMENT_EMAIL = 'recruitment@hipeac.net'


def save_keywords(nl: NaturalLanguageAnalyzer, job: Job):
    job.keywords = json.dumps(nl.get_keywords(' '.join([job.title, job.description])))
    job.processed_at = timezone.now() + datetime.timedelta(seconds=5)
    job.save()


@task()
def process_keywords(job_id: int):
    """Updates keywords for a recently created job."""
    nl = NaturalLanguageAnalyzer()
    job = Job.objects.get(pk=job_id)
    save_keywords(nl, job)


@periodic_task(run_every=crontab(minute=20))
def process_bulk_keywords():
    """Updates keywords for jobs that have been recently created or updated."""
    nl = NaturalLanguageAnalyzer()
    for job in Job.objects.active().filter(Q(processed_at__isnull=True) | Q(updated_at__gt=F('processed_at'))):
        save_keywords(nl, job)


@periodic_task(run_every=crontab(day_of_week='mon-fri', hour=10, minute=0))
def send_expiration_reminders():
    """Sends a tweet and an email when a Job is about to expire."""
    today = timezone.now().date()
    in_five_days = (timezone.now() + timedelta(days=5)).date()
    jobs = Job.objects.filter(deadline__gte=today, deadline__lte=in_five_days, last_reminder__isnull=True)

    for job in jobs:
        tweet.delay(job.get_status('twitter', 'Last days to apply for '))

    send_mail(
        '[HiPEAC Bot] Job expiration reminders sent (10h)',
        'N reminders have been sent to: company1, company2.',
        'noreply@hipeac.net',
        ['eneko@illarra.com'],
        fail_silently=True,
    )


@periodic_task(run_every=crontab(day_of_week='mon-fri', hour=10, minute=0))
def send_evaluations():
    two_weeks_ago = (timezone.now() - timedelta(days=14)).date()
    # jobs = Job.objects.filter(deadline__lte=two_weeks_ago)
    send_mail(
        '[HiPEAC Bot] Job evaluations sent (10h10)',
        'N evalution emails have been sent to: company1, company2.',
        'noreply@hipeac.net',
        ['eneko@illarra.com'],
        fail_silently=True,
    )


@periodic_task(run_every=crontab(day_of_week='fri', hour=10, minute=0))
def send_weekly_digest():
    """Sends a digest to publicity@hipeac.net with the Jobs posted in the last 2 weeks, every two weeks."""
    today = timezone.now().date()
    week_number = int(today.strftime('%U'))
    if week_number % 2 == 0:  # ignore even weeks; @periodic_task doesn't allow this
        return

    send_mail(
        'Latest computing jobs and opportunities (10h)',
        'Includes jobs posted in the last two weeks.',
        JOBS_DIGEST_EMAIL,
        ['eneko@illarra.com'],
        fail_silently=True,
    )


@task()
def share_in_linkedin(title: str, status: Tuple[str, str], thumbnail_url: Optional[str]):
    """Shares a post in LinkedIn."""
    LinkedInManager().share_page(title, *status, thumbnail_url)


@task(rate_limit='10/h')
def tweet(status: Tuple[str, str]):
    """Sends a tweet."""
    Tweeter(account='hipeacjobs').update_status(*status)


"""
from .emails import send_job_reminder, send_job_evaluation
from .models import Job

logger = get_task_logger(__name__)


@periodic_task(run_every=crontab(hour='9', minute='0', day_of_week='mon-fri'))
def send_expiration_reminders():
    today = timezone.now().date()
    in_five_days = (timezone.now() + timedelta(days=5)).date()
    jobs = Job.objects.filter(deadline__gte=today, deadline__lte=in_five_days)
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
