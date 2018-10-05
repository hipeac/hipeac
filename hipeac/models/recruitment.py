from celery.execute import send_task
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

from hipeac.models import Metadata, Permission
from hipeac.validators import validate_no_badwords
from .generic import HipeacCountries
from .mixins import LinkMixin, MetadataMixin, UrlMixin


class JobManager(models.Manager):
    def active(self):
        return self.filter(deadline__gte=timezone.now().date()).order_by('deadline')


class Job(LinkMixin, MetadataMixin, UrlMixin, models.Model):
    """
    A job opening by any HiPEAC institution.
    Jobs are linked to different topics, so that we can send
    personalized information to Users that are interested in those topics.
    """
    route_name = 'job'

    title = models.CharField(max_length=250, validators=[validate_no_badwords])
    description = models.TextField(validators=[validate_no_badwords])
    employment_type = models.ForeignKey(Metadata, null=True, blank=True, on_delete=models.SET_NULL,
                                        limit_choices_to={'field': Metadata.EMPLOYMENT},
                                        related_name=Metadata.EMPLOYMENT)
    deadline = models.DateField(null=True)
    positions = models.PositiveSmallIntegerField(default=1, null=True)

    institution = models.ForeignKey('hipeac.Institution', null=True, blank=False, on_delete=models.SET_NULL,
                                    limit_choices_to={'country__in': HipeacCountries.only}, related_name='jobs')
    project = models.ForeignKey('hipeac.Project', null=True, blank=True, on_delete=models.SET_NULL, related_name='jobs')
    location = models.CharField(max_length=250, null=True, blank=True)
    country = CountryField(db_index=True, null=True, blank=True, countries=HipeacCountries)

    email = models.EmailField(null=True)
    share = models.BooleanField(default=True, editable=False)

    application_areas = models.CharField(max_length=250, default='', validators=[validate_comma_separated_integer_list])
    career_levels = models.CharField(max_length=250, default='', validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, default='', validators=[validate_comma_separated_integer_list])
    links = GenericRelation('hipeac.Link')

    keywords = models.TextField(default='[]', editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='posted_jobs')
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, editable=False)
    reminded_deadline = models.DateField(null=True, blank=True, editable=False)

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
            image_url = instance.institution.images['lg']
        except Exception as e:
            image_url = None

        email = (
            'recruitment.jobs.created',
            f'HiPEAC Job created: "{instance.title}"',
            'HiPEAC Recruitment <recruitment@hipeac.net>',
            [instance.created_by.email],
            {
                'job_title': instance.title,
                'job_pdf_url': instance.get_pdf_url(),
                'user_name': instance.created_by.profile.name,
            }
        )
        send_task('hipeac.tasks.emails.send_from_template', email)
        send_task('hipeac.tasks.recruitment.process_keywords', (instance.id,))
        send_task('hipeac.tasks.recruitment.share_in_linkedin', (instance.title, instance.get_status(), image_url))
        send_task('hipeac.tasks.recruitment.tweet', (instance.get_status('twitter'),))
