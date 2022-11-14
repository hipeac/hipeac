from celery.decorators import periodic_task, task
from celery.schedules import crontab

from hipeac.models import PublicationConference, Profile
from hipeac.tools.dblp import process_conference_publications, process_user_publications


@task(rate_limit="60/m")
def extract_publications_for_conference(conference_id):
    conference = PublicationConference.objects.get(id=conference_id)
    process_conference_publications(conference)


@task(rate_limit="60/m")
def extract_publications_for_user(user_id):
    profile = Profile.objects.prefetch_related("links").get(user_id=user_id)
    process_user_publications(profile)


@periodic_task(run_every=crontab(day_of_week="mon", hour=12, minute=0))
def check_member_publications():
    for profile in Profile.objects.filter(user__member__revocation_date__isnull=True).prefetch_related("links"):
        process_user_publications(profile)
