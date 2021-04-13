from allauth.socialaccount.providers.linkedin_oauth2.provider import LinkedInOAuth2Provider
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, validate_comma_separated_integer_list
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django_countries.fields import CountryField
from hashlib import md5
from typing import Optional

from hipeac.functions import get_images_path, send_task
from hipeac.models import Metadata
from .mixins import ImagesMixin, LinkMixin, MetadataMixin


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
        "female",
        "male",
    ]
    incompatible = [("member", "affiliated"), ("nms", "non-eu"), ("female", "male")]
    tags = value.split(",")
    for tag in tags:
        if tag not in valid:
            raise ValidationError(f'"{tag}" is not a valid membership tag.')
    for t in incompatible:
        if len(set(t).intersection(tags)) > 1:
            raise ValidationError(f'Only one of the following can be set: "{",".join(t)}".')


class ProfileQuerySet(models.QuerySet):
    def active(self):
        return self.filter(user__is_active=True)

    def public(self):
        return self.filter(user__is_active=True, is_public=True)


class ProfileManager(models.Manager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).select_related("user", "gender", "title", "meal_preference")

    def active(self):
        return self.get_queryset().active()

    def public(self):
        return self.get_queryset().public()


class Profile(ImagesMixin, LinkMixin, MetadataMixin, models.Model):
    """
    Extends Django User model with extra profile fields.
    """

    user = models.OneToOneField(get_user_model(), related_name="profile", primary_key=True, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
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
    department = models.CharField(max_length=200, null=True, blank=True)
    institution = models.ForeignKey(
        "hipeac.Institution", null=True, blank=True, on_delete=models.SET_NULL, related_name="profiles"
    )
    second_institution = models.ForeignKey(
        "hipeac.Institution", null=True, blank=True, on_delete=models.SET_NULL, related_name="second_profiles"
    )
    image = models.FileField(
        "Avatar",
        upload_to=get_images_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg"])],
    )

    membership_tags = models.CharField(max_length=150, null=True, blank=True, validators=[validate_membership_tags])
    membership_date = models.DateField(null=True, blank=True)
    membership_revocation_date = models.DateField(null=True, blank=True)
    advisor = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name="affiliates",
        null=True,
        blank=True,
        limit_choices_to={"profile__membership_tags__contains": "member"},
    )

    is_bouncing = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    application_areas = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    projects = models.ManyToManyField("hipeac.Project", blank=True, related_name="profiles")
    links = GenericRelation("hipeac.Link")

    updated_at = models.DateTimeField(auto_now=True)

    objects = ProfileManager()

    class Meta:
        indexes = [
            models.Index(fields=["membership_tags"]),
        ]

    def clean(self):
        """
        Validates the model before saving.
        """
        if self.membership_tags == "":
            self.membership_date = None
            self.advisor = None
        else:
            if "member" in self.membership_tags:
                self.advisor = None
                if self.membership_date is None:
                    raise ValidationError("A membership date is required for members.")
            if "affiliated" in self.membership_tags and self.advisor is None:
                raise ValidationError("Please select an advisor for this membership type.")

    def save(self, *args, **kwargs):
        if self.membership_tags:
            self.membership_tags = ",".join(sorted([tag.strip() for tag in self.membership_tags.split(",")]))
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.user.username

    @property
    def email(self) -> str:
        return self.user.email

    @property
    def username(self) -> str:
        return self.user.username

    @property
    def name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

    @cached_property
    def avatar_url(self, size: int = 80) -> str:
        try:
            if self.images:
                return self.images["sm"]

            email_hash = md5(self.user.email.lower().encode("utf-8")).hexdigest()
        except Exception:
            email_hash = md5("hipeac@hipeac.net".encode("utf-8")).hexdigest()

        return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=retro&r=PG"

    def get_absolute_url(self) -> str:
        return reverse("user", args=[self.username])

    @property
    def membership(self) -> Optional[str]:
        if not self.membership_tags:
            return None
        if "affiliated" in self.membership_tags:
            return "affiliated member"
        if "member" in self.membership_tags and not self.membership_revocation_date:
            return "member"
        return None

    def is_member(self) -> bool:
        return self.membership == "member"

    def is_steering_member(self) -> bool:
        return self.user.groups.filter(name="Steering Committee").exists()


@receiver(post_save, sender=Profile)
def post_save_profile(sender, instance, created, **kwargs):
    if instance.image_has_changed():
        send_task("hipeac.tasks.imaging.generate_avatar_variants", (instance.image.path,))


@receiver(post_save, sender=get_user_model())
def post_save_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.updated_at = timezone.now()
        instance.profile.save()


@receiver(social_account_added)
def social_account_added(request, sociallogin, **kwargs):
    if sociallogin and sociallogin.account.provider == LinkedInOAuth2Provider.id:
        from hipeac.tools.notifications.users import LinkedInNotificator

        LinkedInNotificator().deleteOne(user_id=sociallogin.user.id)
