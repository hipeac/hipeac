from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone

from hipeac.functions import get_images_path, send_task
from hipeac.validators import validate_no_badwords
from .mixins import (
    ApplicationAreasMixin,
    EditorMixin,
    ImageMixin,
    InstitutionsMixin,
    KeywordsMixin,
    LinksMixin,
    PermissionsMixin,
    TopicsMixin,
)
from .metadata import Metadata


class ProjectManager(models.Manager):
    ERC_PROGRAMME = 88
    OTHER = 87

    def erc_only(self):
        return self.get_queryset().filter(programme=self.ERC_PROGRAMME).order_by("-start_date")

    def non_erc(self):
        return self.get_queryset().exclude(programme__in=[self.ERC_PROGRAMME, self.OTHER]).order_by("-start_date")


class Project(
    ApplicationAreasMixin,
    EditorMixin,
    ImageMixin,
    InstitutionsMixin,
    KeywordsMixin,
    LinksMixin,
    PermissionsMixin,
    TopicsMixin,
    models.Model,
):
    """
    FP7/H2020 projects related to HiPEAC.
    """

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    name = models.CharField(max_length=8)
    acronym = models.CharField(max_length=50)
    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True, validators=[validate_no_badwords])
    coordinator = models.ForeignKey(
        get_user_model(), null=True, blank=True, on_delete=models.SET_NULL, related_name="coordinated_projects"
    )
    coordinating_institution = models.ForeignKey(
        "hipeac.Institution", null=True, on_delete=models.SET_NULL, related_name="coordinated_projects"
    )
    communication_officer = models.ForeignKey(
        get_user_model(), null=True, blank=True, on_delete=models.SET_NULL, related_name="communicating_projects"
    )
    programme = models.ForeignKey(
        Metadata,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"type": Metadata.PROJECT_PROGRAMME},
        related_name="project_" + Metadata.PROJECT_PROGRAMME,
    )

    image = models.FileField(
        "logo",
        upload_to=get_images_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["png"])],
    )

    updated_at = models.DateTimeField(auto_now=True)

    objects = ProjectManager()

    class Meta:
        ordering = ("acronym",)

    def __str__(self) -> str:
        return self.acronym

    def get_absolute_url(self) -> str:
        return reverse("project", args=[self.id, self.slug])

    def is_active(self) -> bool:
        try:
            return self.start_date <= timezone.now().date() <= self.end_date
        except Exception:
            return False

    @property
    def ec_project_id(self) -> int:
        return None  # TODO: get from Cordis URL

    @property
    def full_name(self) -> str:
        return f"{self.acronym}: {self.name}"  # pragma: no cover

    @property
    def partners(self):
        return self.institutions

    @property
    def short_name(self) -> str:
        return f"{self.acronym} ({self.programme} project)"  # pragma: no cover

    @property
    def slug(self) -> str:
        return slugify(self.acronym)


@receiver(post_save, sender=Project)
def project_post_save(sender, instance, created, *args, **kwargs):
    if instance.image_has_changed():
        send_task("hipeac.tasks.imaging.generate_logo_variants", (instance.image.path,))


class RelatedProject(models.Model):
    PUBLIC = "public"
    PRIVATE = "private"
    TYPE_CHOICES = (
        (PUBLIC, "Public"),
        (PRIVATE, "Private"),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="projects")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        db_table = "hipeac_rel_project"
        ordering = ("content_type", "object_id", "project__acronym")
        unique_together = ("content_type", "object_id", "project")
