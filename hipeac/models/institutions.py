from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django_countries.fields import CountryField

from hipeac.functions import get_images_path, send_task
from hipeac.validators import validate_no_badwords
from .mixins import ApplicationAreasMixin, EditorMixin, ImageMixin, LinksMixin, PermissionsMixin, TopicsMixin
from .permissions import Permission


class Institution(
    ApplicationAreasMixin, EditorMixin, ImageMixin, LinksMixin, PermissionsMixin, TopicsMixin, models.Model
):
    """
    Any institution related to HiPEAC. Institutions are used to determine user affiliation,
    or for managing institution level information like job offers.
    """

    UNIVERSITY = "university"
    LAB = "lab"
    INNOVATION = "innovation"
    INDUSTRY = "industry"
    SME = "sme"
    OTHER = "other"
    TYPE_CHOICES = (
        (UNIVERSITY, "University"),
        (LAB, "Government Lab"),
        (INNOVATION, "Innovation Center"),
        (INDUSTRY, "Industry"),
        (SME, "SME"),
        (OTHER, "Other"),
    )
    ALL_INDUSTRY = (INDUSTRY, SME)

    name = models.CharField(max_length=190)
    local_name = models.CharField(max_length=190, null=True, blank=True)
    colloquial_name = models.CharField(max_length=30, null=True, blank=True)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    location = models.CharField(max_length=100, null=True, blank=True)
    country = CountryField(db_index=True)
    description = models.TextField(null=True, blank=True, validators=[validate_no_badwords])
    recruitment_contact = models.CharField(max_length=190, null=True, blank=True)
    recruitment_email = models.EmailField(null=True, blank=True)

    image = models.FileField(
        "logo",
        upload_to=get_images_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["png"])],
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        if self.country:
            return f"{self.name}, {self.country.name}"
        return self.name

    def can_be_managed_by(self, user) -> bool:
        return self.acl.filter(user_id=user.id, level__gte=Permission.ADMIN).exists()

    def get_absolute_url(self) -> str:
        return reverse("institution", args=[self.id, self.slug])

    @property
    def schema_org_type(self) -> str:
        return {
            self.UNIVERSITY: "EducationalOrganization",
            self.LAB: "GovernmentOrganization",
            self.INNOVATION: "GovernmentOrganization",
            self.INDUSTRY: "Corporation",
            self.SME: "Corporation",
            self.OTHER: "Organization",
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
        send_task("hipeac.tasks.imaging.generate_logo_variants", (instance.image.path,))


class RelatedInstitution(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="institutions")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    class Meta:
        db_table = "hipeac_rel_institution"
        ordering = ("content_type", "object_id", "institution__name")
        unique_together = ("content_type", "object_id", "institution")
