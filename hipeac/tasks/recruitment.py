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
from .emails import JOBS_DIGEST_EMAIL, RECRUITMENT_EMAIL, send_from_template


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
    jobs = Job.objects.filter(deadline__gte=today, deadline__lte=in_five_days).filter(
        Q(reminder_sent_for__isnull=True) | Q(reminder_sent_for__lt=F('deadline'))
    ).select_related('institution', 'created_by__profile')

    # send tweets
    for job in jobs:
        tweet(job.get_status('twitter', 'Last days to apply for '))

    # send emails
    for key, context_data in Job.objects.grouped_for_email(jobs).items():
        send_from_template(
            'recruitment.jobs.expiration_reminder',
            f'[HiPEAC Jobs] Expiring vacancies @ {context_data["institution_name"]}',
            RECRUITMENT_EMAIL,
            [context_data['user_email']],
            context_data,
        )
        for job in context_data['jobs']:
            j = Job.objects.get(id=job['id'])
            j.reminder_sent_for = j.deadline
            j.save()


@periodic_task(run_every=crontab(day_of_week='mon-fri', hour=11, minute=0))
def send_evaluations():
    two_weeks_ago = (timezone.now() - timedelta(days=14)).date()
    jobs = Job.objects.filter(deadline__lte=two_weeks_ago, evaluation_sent_for__isnull=True) \
                      .select_related('institution', 'created_by__profile')

    # send emails
    for key, context_data in Job.objects.grouped_for_email(jobs).items():
        send_from_template(
            'recruitment.jobs.evaluation',
            f'[HiPEAC Jobs] Satisfaction survey @ {context_data["institution_name"]}',
            RECRUITMENT_EMAIL,
            ['eneko@illarra.com'],  # TODO: update
            context_data,
        )
        for job in context_data['jobs']:
            j = Job.objects.get(id=job['id'])
            j.evaluation_sent_for = j.deadline
            j.save()


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


@task(rate_limit='6/h')
def share_in_linkedin(title: str, status: Tuple[str, str], thumbnail_url: Optional[str]):
    """Shares a post in LinkedIn."""
    LinkedInManager().share_page(title, *status, thumbnail_url)


@task(rate_limit='6/h')
def tweet(status: Tuple[str, str]):
    """Sends a tweet."""
    Tweeter(account='hipeacjobs').update_status(*status)
