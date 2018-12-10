from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField
from typing import Tuple

from hipeac.functions import send_task
from hipeac.models import Metadata, Permission
from hipeac.validators import validate_no_badwords
from .generic import HipeacCountries
from .mixins import LinkMixin, MetadataMixin, EditorMixin, UrlMixin


class JobManager(models.Manager):
    def active(self):
        return self.filter(deadline__gte=timezone.now().date()).order_by('deadline')

    @staticmethod
    def grouped_for_email(queryset) -> dict:
        grouped_jobs = {}

        for job in queryset:
            key = (job.created_by_id, job.institution_id)
            if key not in grouped_jobs:
                grouped_jobs[key] = {
                    'user_email': job.created_by.email,
                    'user_name': job.created_by.profile.name,
                    'institution_name': job.institution.short_name if job.institution else 'your institution',
                    'jobs': []
                }
            job_evaluation_url = reverse('job_evaluation', args=[job.id, 0])
            grouped_jobs[key]['jobs'].append({
                'id': job.id,
                'title': job.title,
                'editor_url': job.get_editor_url(),
                'no_url': job_evaluation_url.replace('/0/', f'/{JobEvaluation.NO}/'),
                'yes_url': job_evaluation_url.replace('/0/', f'/{JobEvaluation.YES}/'),
                'yes_hipeac_url': job_evaluation_url.replace('/0/', f'/{JobEvaluation.YES_HIPEAC}/'),
            })

        return grouped_jobs


class Job(LinkMixin, MetadataMixin, UrlMixin, models.Model):
    """
    A job opening by any HiPEAC institution.
    Jobs are linked to different topics, so that we can send
    personalized information to Users that are interested in those topics.
    """
    route_name = 'job'

    title = models.CharField(max_length=250, validators=[validate_no_badwords])
    description = models.TextField(validators=[validate_no_badwords])
    employment_type = models.ForeignKey(Metadata, null=True, blank=False, on_delete=models.SET_NULL,
                                        limit_choices_to={'type': Metadata.EMPLOYMENT},
                                        related_name=Metadata.EMPLOYMENT)
    deadline = models.DateField(null=True)
    positions = models.PositiveSmallIntegerField(default=1, null=True)

    institution = models.ForeignKey('hipeac.Institution', null=True, blank=False, on_delete=models.SET_NULL,
                                    related_name='jobs')
    project = models.ForeignKey('hipeac.Project', null=True, blank=True, on_delete=models.SET_NULL, related_name='jobs')
    location = models.CharField(max_length=250, null=True, blank=True)
    country = CountryField(db_index=True, null=True, blank=True, countries=HipeacCountries)

    email = models.EmailField(null=True, blank=False)
    share = models.BooleanField(default=True, editable=False)

    application_areas = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    career_levels = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    links = GenericRelation('hipeac.Link')

    keywords = models.TextField(default='[]', editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='posted_jobs')
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, editable=False)
    reminder_sent_for = models.DateField(null=True, blank=True, editable=False)
    evaluation_sent_for = models.DateField(null=True, blank=True, editable=False)

    objects = JobManager()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.title

    def can_be_managed_by(self, user) -> bool:
        return (
            self.created_by_id == user.id or
            self.institution.acl.filter(user_id=user.id, level__gte=Permission.ADMIN).exists()
        )

    def deadline_is_near(self) -> bool:
        return (self.deadline - timezone.now().date()).days < 7

    def get_absolute_url(self) -> str:
        return reverse('job', args=[self.id, self.slug])

    def get_pdf_url(self) -> str:
        return reverse('job_pdf', args=[self.id])

    def get_short_url(self) -> str:
        return reverse('job_redirect', args=[self.id])

    def get_status(self, social_media: str = 'any', prepend: str = '') -> Tuple[str, str]:
        at = ''
        url = f'https://www.hipeac.net{self.get_absolute_url()}'

        if self.institution:
            at = f' at #{"".join(self.institution.short_name.split())}'

            if social_media == 'twitter' and self.institution.twitter_username:
                at = f' at @{self.institution.twitter_username}'
                url = f'hipeac.net{self.get_short_url()}'

        return f'{prepend}#job{at}: {self.title}', url

    @property
    def slug(self) -> str:
        return slugify(self.title)


@receiver(post_save, sender=Job)
def job_post_save(sender, instance, created, *args, **kwargs):
    if created:
        try:
            image_url = instance.institution.images['th']
        except Exception:
            image_url = None

        email = (
            'recruitment.jobs.created',
            f'HiPEAC Job created: "{instance.title}"',
            'HiPEAC Recruitment <recruitment@hipeac.net>',
            [instance.created_by.email],
            {
                'job_url': instance.get_absolute_url(),
                'job_title': instance.title,
                'job_pdf_url': instance.get_pdf_url(),
                'user_name': instance.created_by.profile.name,
            }
        )
        send_task('hipeac.tasks.emails.send_from_template', email)
        send_task('hipeac.tasks.recruitment.process_keywords', (instance.id,))
        send_task('hipeac.tasks.recruitment.share_in_linkedin', (instance.title, instance.get_status(), image_url))
        send_task('hipeac.tasks.recruitment.tweet', (instance.get_status('twitter'),))


class JobEvaluation(EditorMixin, models.Model):
    """
    A job evaluation.
    """
    NO = 0
    YES = 2
    YES_HIPEAC = 1
    VALUE_CHOICES = (
        (NO, 'No'),
        (YES, 'Yes'),
        (YES_HIPEAC, 'Yes, via the HiPEAC Jobs portal!'),
    )

    job = models.OneToOneField(Job, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    comments = models.TextField(null=True, blank=True)
    selected_candidate = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.job.title

    def can_be_managed_by(self, user) -> bool:
        return (
            self.job.created_by_id == user.id or
            self.job.institution.acl.filter(user_id=user.id, level__gte=Permission.ADMIN).exists()
        )
