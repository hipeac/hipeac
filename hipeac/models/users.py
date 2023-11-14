from allauth.socialaccount.providers.linkedin_oauth2.provider import LinkedInOAuth2Provider
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django_countries.fields import CountryField
from hashlib import md5

from hipeac.functions import get_images_path, send_task
from .metadata import Metadata
from .mixins import ApplicationAreasMixin, FilesMixin, ImageMixin, LinksMixin, ProjectsMixin, TopicsMixin


User = get_user_model()


def validate_membership_tags(value: str):
    valid = [
        "member",
        "affiliated",
        "phd",
        "staff",
        "nms",
        "non-eu",
        "innovation",
        "industry",
        "stakeholder",
    ]
    incompatible = [("member", "affiliated"), ("nms", "non-eu")]
    tags = value.split(",")
    for tag in tags:
        if tag not in valid:
            raise ValidationError(f'"{tag}" is not a valid membership tag.')
    for t in incompatible:
        if len(set(t).intersection(tags)) > 1:
            raise ValidationError(f'Only one of the following can be set: "{",".join(t)}".')


class RelatedUser(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="speakers")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "hipeac_rel_user"
        ordering = ("content_type", "object_id")
        unique_together = ("content_type", "object_id", "user")


class ProfileQuerySet(models.QuerySet):
    def active(self):
        return self.filter(user__is_active=True)

    def public(self):
        return self.filter(user__is_active=True, is_public=True)


class Profile(ApplicationAreasMixin, FilesMixin, ImageMixin, LinksMixin, ProjectsMixin, TopicsMixin, models.Model):
    """
    Extends Django User model with extra profile fields.
    """

    user = models.OneToOneField(User, related_name="profile", primary_key=True, on_delete=models.CASCADE)
    country = CountryField(db_index=True)
    gender = models.ForeignKey(
        Metadata,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"type": Metadata.GENDER},
        related_name=Metadata.GENDER,
    )
    title = models.ForeignKey(
        Metadata,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"type": Metadata.TITLE},
        related_name="user_" + Metadata.TITLE,
    )
    meal_preference = models.ForeignKey(
        Metadata,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"type": Metadata.MEAL_PREFERENCE},
        related_name="user_" + Metadata.MEAL_PREFERENCE,
    )
    position = models.ForeignKey(
        Metadata,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"type": Metadata.JOB_POSITION},
        related_name="user_" + Metadata.JOB_POSITION,
    )
    institution = models.ForeignKey(
        "hipeac.Institution", null=True, blank=True, on_delete=models.SET_NULL, related_name="profiles"
    )
    second_institution = models.ForeignKey(
        "hipeac.Institution", null=True, blank=True, on_delete=models.SET_NULL, related_name="second_profiles"
    )
    bio = models.TextField(null=True, blank=True)
    image = models.FileField(
        "Avatar",
        upload_to=get_images_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg"])],
    )

    is_bouncing = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    objects = ProfileQuerySet.as_manager()

    def __str__(self) -> str:
        return f"{self.name} ({self.username})"

    def get_absolute_url(self) -> str:
        try:
            return reverse("user", args=[self.username])
        except Exception:
            return reverse("homepage")

    def is_member(self) -> bool:
        return getattr(self, "member", None) is not None

    @cached_property
    def is_steering_member(self) -> bool:
        return self.user.groups.filter(name="Steering Committee").exists()

    @property
    def email(self) -> str:
        return self.user.email

    @property
    def name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def username(self) -> str:
        return self.user.username

    @cached_property
    def avatar_url(self, size: int = 80) -> str:
        try:
            if self.images:
                return self.images["sm"]

            email_hash = md5(self.user.email.lower().encode("utf-8")).hexdigest()
        except Exception:
            email_hash = md5("hipeac@hipeac.net".encode("utf-8")).hexdigest()

        return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=retro&r=PG"

    def membership_tags(self) -> list:
        return []

    @cached_property
    def cv(self) -> "hipeac.File":
        return self.files.filter(keywords__contains=["cv"]).first()

    def files_viewable_by_user(self, user) -> bool:
        if self.user_id == user.id:
            return True

        fair_job_ids = self.user.job_fair_registrations.values_list("jobs", flat=True)
        recruiter_job_ids = user.job_fairs.values_list("institution__jobs", flat=True)
        intersection = set(fair_job_ids).intersection(set(recruiter_job_ids))
        return len(intersection) > 0


@receiver(post_delete, sender=User)
def post_delete_user(sender, instance, *args, **kwargs):
    send_task("hipeac.tasks.db.refresh_member_view")


@receiver(post_save, sender=User)
def post_save_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, updated_at=timezone.now())
    else:
        instance.profile.updated_at = timezone.now()
        instance.profile.save()


@receiver(post_save, sender=Profile)
def post_save_profile(sender, instance, created, **kwargs):
    if instance.image_has_changed():
        send_task("hipeac.tasks.imaging.generate_avatar_variants", (instance.image.path,))


@receiver(social_account_added)
def post_social_account_added(request, sociallogin, **kwargs):
    if sociallogin and sociallogin.account.provider == LinkedInOAuth2Provider.id:
        from hipeac.tools.notifications.users import LinkedInNotificator

        LinkedInNotificator().deleteOne(user_id=sociallogin.user.id)
