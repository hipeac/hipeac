from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField
from typing import Tuple

from hipeac.models import Institution, Metadata, Permission
from hipeac.models.countries import HipeacCountries
from hipeac.validators import validate_no_badwords
from ..mixins import ApplicationAreasMixin, EditorMixin, KeywordsMixin, LinksMixin, TopicsMixin


def validate_institution(institution, user) -> None:
    if user.is_staff or user.groups.filter(name="External recruiters").exists():
        return

    try:
        institution = Institution.objects.get(id=institution["id"])
    except Institution.DoesNotExist:
        raise ValidationError("Institution does not exist.")

    ids = [institution.id] + list(institution.children.values_list("id", flat=True))
    if institution.parent_id:
        ids.append(institution.parent_id)
    if user.profile.institution_id not in ids and user.profile.second_institution_id not in ids:
        raise ValidationError("You can only create a job position for your institution. Please check your affiliation.")


class JobManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "career_levels",
                "employment_type",
                "rel_application_areas__application_area",
                "rel_topics__topic",
            )
        )

    def active(self):
        return self.get_queryset().filter(deadline__gte=timezone.now().date()).order_by("deadline")

    def active_internships(self):
        return self.get_queryset().filter(deadline__gte=timezone.now().date(), employment_type=17).order_by("deadline")


class Job(ApplicationAreasMixin, EditorMixin, KeywordsMixin, LinksMixin, TopicsMixin, models.Model):
    """
    A job opening by any HiPEAC institution.
    Jobs are linked to different topics, so that we can send
    personalized information to Users that are interested in those topics.
    """

    institution = models.ForeignKey(
        "hipeac.Institution", null=True, blank=False, on_delete=models.SET_NULL, related_name="jobs"
    )
    project = models.ForeignKey("hipeac.Project", null=True, blank=True, on_delete=models.SET_NULL, related_name="jobs")
    employment_type = models.ForeignKey(
        Metadata,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        limit_choices_to={"type": Metadata.EMPLOYMENT},
        related_name="employment_type",
    )
    career_levels = models.ManyToManyField(
        Metadata,
        limit_choices_to={"type": Metadata.JOB_POSITION},
        related_name="career_levels",
    )
    title = models.CharField(max_length=250, validators=[validate_no_badwords])
    description = models.TextField(validators=[validate_no_badwords])
    location = models.CharField(max_length=250, null=True, blank=True)
    country = CountryField(db_index=True, null=True, blank=True, countries=HipeacCountries)
    deadline = models.DateField(null=True)
    positions = models.PositiveSmallIntegerField(default=1, null=True)
    email = models.EmailField(null=True, blank=True)
    share = models.BooleanField(default=True, editable=False)
    add_to_euraxess = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="posted_jobs"
    )
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, editable=False)
    reminder_sent_for = models.DateField(null=True, blank=True, editable=False)
    evaluation_sent_for = models.DateField(null=True, blank=True, editable=False)

    objects = JobManager()

    class Meta:
        ordering = ("-id",)

    def __str__(self) -> str:
        return self.title

    def can_be_managed_by(self, user) -> bool:
        return (
            self.created_by_id == user.id
            or self.institution.acl.filter(user_id=user.id, level__gte=Permission.ADMIN).exists()
        )

    def deadline_is_near(self) -> bool:
        return (self.deadline - timezone.now().date()).days < 7 if self.deadline else False

    def is_closed(self) -> bool:
        return self.deadline < timezone.now().date() if self.deadline else False

    def get_absolute_url(self) -> str:
        return reverse("job", args=[self.id, self.slug])

    def get_pdf_url(self) -> str:
        return reverse("job_pdf", args=[self.id])

    def get_short_url(self) -> str:
        return reverse("job_redirect", args=[self.id])

    def get_career_levels_display(self, separator: str = ", ") -> str:
        values = [obj.value for obj in self.career_levels.all()]
        values.sort()
        return separator.join(values)

    def get_status(self, social_media: str = "any", prepend: str = "") -> Tuple[str, str]:
        at = ""
        url = f"https://www.hipeac.net{self.get_absolute_url()}"
        hashtag = "#internship" if self.employment_type.value == "Internship" else "#job"

        if self.institution:
            at = f' at #{"".join(self.institution.short_name.split())}'

            if social_media == "twitter" and self.institution.twitter_username:
                at = f" at @{self.institution.twitter_username}"
                url = f"hipeac.net{self.get_short_url()}"

        return f"{prepend}{hashtag}{at}: {self.title}", url

    @property
    def institution_type(self) -> str:
        return self.institution.type if self.institution else ""

    @property
    def slug(self) -> str:
        return slugify(self.title)


@receiver(post_save, sender=Job)
def job_post_save(sender, instance, created, *args, **kwargs):
    if created:
        pass
        """
        try:
            image_url = instance.institution.images["th"]
        except Exception:
            image_url = None

        email = (
            "recruitment.jobs.created",
            f'HiPEAC Job created: "{instance.title}"',
            "HiPEAC Recruitment <recruitment@hipeac.net>",
            [instance.created_by.email],
            {
                "job_url": instance.get_absolute_url(),
                "job_title": instance.title,
                "job_pdf_url": instance.get_pdf_url(),
                "user_name": instance.created_by.profile.name,
                "show_euraxess": instance.add_to_euraxess,
            },
        )
        send_task("hipeac.tasks.emails.send_from_template", email)
        send_task("hipeac.tasks.recruitment.process_keywords", (instance.id,))
        send_task("hipeac.tasks.recruitment.share_in_linkedin", (instance.title, instance.get_status(), image_url))
        send_task("hipeac.tasks.recruitment.tweet", (instance.get_status("twitter"),))
        """
