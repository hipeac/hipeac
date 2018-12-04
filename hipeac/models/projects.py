from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import FileExtensionValidator, validate_comma_separated_integer_list
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone

from hipeac.functions import get_images_path, send_task
from hipeac.models import Permission
from hipeac.validators import validate_no_badwords
from .mixins import ImagesMixin, LinkMixin, UrlMixin


class Project(ImagesMixin, LinkMixin, UrlMixin, models.Model):
    """
    FP7/H2020 projects related to HiPEAC.
    """
    route_name = 'project'
    ASSETS_FOLDER = 'raw/projects'

    PROGRAMME_CHOICES = (
        ('FP7', 'FP7'),
        ('H2020', 'H2020'),
    )

    programme = models.CharField(max_length=5, null=True, blank=True, choices=PROGRAMME_CHOICES)
    acronym = models.CharField(max_length=50)
    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True, validators=[validate_no_badwords])
    coordinator = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='coordinated_projects')
    coordinating_institution = models.ForeignKey('hipeac.Institution', null=True, on_delete=models.SET_NULL,
                                                 related_name='coordinated_projects')
    partners = models.ManyToManyField('hipeac.Institution', blank=True, related_name='participated_projects')
    communication_officer = models.ForeignKey(get_user_model(), null=True, blank=True,
                                              on_delete=models.SET_NULL, related_name='communicating_projects')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    ec_project_id = models.PositiveIntegerField('Project ID', unique=True, null=True, blank=True)
    project_officer = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL,
                                        related_name='officed_projects')
    image = models.FileField('Logo', upload_to=get_images_path, null=True, blank=True,
                             validators=[FileExtensionValidator(allowed_extensions=['png'])])
    poster_file = models.FileField('Poster', upload_to=ASSETS_FOLDER, null=True, blank=True)

    application_areas = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    acl = GenericRelation('hipeac.Permission')
    links = GenericRelation('hipeac.Link')

    keywords = models.TextField(null=True, blank=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['acronym']

    def __str__(self) -> str:
        return self.acronym

    def can_be_managed_by(self, user) -> bool:
        return self.acl.filter(user_id=user.id, level__gte=Permission.ADMIN).exists()

    @property
    def full_name(self) -> str:
        return f'{self.acronym}: {self.name}'  # pragma: no cover

    def is_active(self) -> bool:
        try:
            return self.start_date <= timezone.now().date() <= self.end_date
        except Exception:
            return False

    @property
    def short_name(self) -> str:
        return f'{self.acronym} ({self.get_programme_display()} project)'  # pragma: no cover

    @property
    def slug(self) -> str:
        return slugify(self.acronym)


@receiver(post_save, sender=Project)
def project_post_save(sender, instance, created, *args, **kwargs):
    if instance.image_has_changed():
        send_task('hipeac.tasks.imaging.generate_logo_variants', (instance.image.path,))
