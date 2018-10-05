from celery.execute import send_task
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django_countries.fields import CountryField

from hipeac.functions import get_images_path
from hipeac.models import Permission
from hipeac.validators import validate_no_badwords
from .mixins import ImagesMixin, LinkMixin, UrlMixin


class Institution(ImagesMixin, LinkMixin, UrlMixin, models.Model):
    """
    Any institution related to HiPEAC. Institutions are used to determine user affiliation,
    or for managing institution level information like job offers.
    """
    route_name = 'institution'

    UNIVERSITY = 'university'
    LAB = 'lab'
    INNOVATION = 'innovation'
    INDUSTRY = 'industry'
    SME = 'sme'
    OTHER = 'other'
    TYPE_CHOICES = (
        (UNIVERSITY, 'University'),
        (LAB, 'Government Lab'),
        (INNOVATION, 'Innovation Center'),
        (INDUSTRY, 'Industry'),
        (SME, 'SME'),
        (OTHER, 'Other'),
    )
    ALL_INDUSTRY = (INDUSTRY, SME)

    name = models.CharField(max_length=190)
    local_name = models.CharField(max_length=190, null=True, blank=True)
    colloquial_name = models.CharField(max_length=30, null=True, blank=True)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    location = models.CharField(max_length=100, null=True, blank=True)
    country = CountryField(db_index=True)
    description = models.TextField(null=True, blank=True, validators=[validate_no_badwords])
    recruitment_contact = models.CharField(max_length=190, null=True, blank=True)
    recruitment_email = models.EmailField(null=True, blank=True)
    image = models.FileField('Logo', upload_to=get_images_path, null=True, blank=True)

    application_areas = models.CharField(max_length=250, default='', validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, default='', validators=[validate_comma_separated_integer_list])
    acl = GenericRelation('hipeac.Permission')
    links = GenericRelation('hipeac.Link')

    updated_at = models.DateTimeField()  # auto_now=True

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.short_name

    def can_be_managed_by(self, user) -> bool:
        return self.acl.filter(user_id=user.id, level__gte=Permission.ADMIN).exists()

    @property
    def schema_org_type(self) -> str:
        return {
            self.UNIVERSITY: 'EducationalOrganization',
            self.LAB: 'GovernmentOrganization',
            self.INDUSTRY: 'Corporation',
            self.SME: 'Corporation',
            self.OTHER: 'Organization',
        }[self.type]

    @property
    def short_name(self) -> str:
        return self.colloquial_name if self.colloquial_name else self.name

    @property
    def slug(self) -> str:
        return slugify(self.short_name)


@receiver(post_save, sender=Institution)
def institution_post_save(sender, instance, created, *args, **kwargs):
    if instance.image_has_changed():
        send_task('hipeac.tasks.imaging.generate_logo_variants', (instance.image.path,))
