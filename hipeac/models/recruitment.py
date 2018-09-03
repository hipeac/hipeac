from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone
from django_countries.fields import CountryField

from hipeac.functions import HipeacCountries
from hipeac.models import Metadata
from hipeac.validators import validate_no_badwords
from .mixins import ContentTypeMixin, LinkMixin, UrlMixin


class JobManager(models.Manager):
    def active(self):
        return self.filter(deadline__gte=timezone.now().date()).order_by('deadline')


class Job(LinkMixin, UrlMixin, ContentTypeMixin, models.Model):
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

    keywords = models.TextField(null=True, blank=True, editable=False)
    last_reminder = models.DateTimeField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)  # TODO: auto_now_add=True
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='posted_jobs')
    updated_at = models.DateTimeField(auto_now=True)  # TODO: auto_now=True

    objects = JobManager()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.title

    def deadline_is_near(self) -> bool:
        return (self.deadline - timezone.now().date()).days < 7

    @property
    def slug(self) -> str:
        return slugify(self.title)


@receiver(post_save, sender=Job)
def job_post_save(sender, instance, created, *args, **kwargs):
    if created:
        # send_task('hipeac.tasks.twitter.tweet', ('message',))
        pass
