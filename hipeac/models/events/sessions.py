from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from hipeac.models import Metadata, Permission
from .events import validate_date
from ..mixins import LinkMixin


class SessionAbstractModel(models.Model):
    event = None
    session_type = models.ForeignKey(
        Metadata,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        limit_choices_to={"type": Metadata.SESSION_TYPE},
        related_name=f"%(class)ss_{Metadata.SESSION_TYPE}",
    )
    is_private = models.BooleanField(default=False)

    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=250)
    organizers = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    program = models.TextField(null=True, blank=True)
    main_speaker = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="main_%(class)ss",
        related_query_name="%(app_label)s_%(class)ss",
    )
    speakers = models.ManyToManyField(
        get_user_model(), blank=True, related_name="%(class)ss", related_query_name="%(app_label)s_%(class)ss"
    )
    keywords = models.JSONField(default=list, editable=False)

    application_areas = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    projects = models.ManyToManyField(
        "hipeac.Project", blank=True, related_name="%(class)ss", related_query_name="%(app_label)s_%(class)ss"
    )
    institutions = models.ManyToManyField(
        "hipeac.Institution", blank=True, related_name="%(class)ss", related_query_name="%(app_label)s_%(class)ss"
    )

    zoom_webinar_id = models.CharField(max_length=32, null=True, blank=True)
    zoom_attendee_report = models.FileField(upload_to="private/zoom", null=True, blank=True)

    acl = GenericRelation("hipeac.Permission")
    links = GenericRelation("hipeac.Link")
    private_files = GenericRelation("hipeac.PrivateFile")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def clean(self) -> None:
        if self.event:
            validate_date(self.start_at.date(), self.event)

    def __str__(self) -> str:
        return self.title

    def can_be_managed_by(self, user) -> bool:
        return self.main_speaker_id == user.id or self.acl.filter(user_id=user.id, level__gte=Permission.ADMIN).exists()

    def get_editor_url(self) -> str:
        content_type = ContentType.objects.get_for_model(self)
        return reverse("editor", args=[content_type.id, self.id])

    @property
    def is_industrial_session(self) -> bool:
        return self.session_type.value == "Industrial Session"

    @property
    def slug(self) -> str:
        return slugify(self.title)

    @property
    def zoom_webinar_int(self) -> int:
        return int(self.zoom_webinar_id.replace(" ", ""))


class Session(LinkMixin, SessionAbstractModel):
    event = models.ForeignKey("hipeac.Event", on_delete=models.CASCADE, related_name="sessions")

    room = models.ForeignKey("hipeac.Room", null=True, blank=True, on_delete=models.SET_NULL, related_name="sessions")
    max_attendees = models.PositiveSmallIntegerField(default=0, help_text="Leave on `0` for non limiting.")
    extra_attendees_fee = models.PositiveSmallIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.id:
            self.keywords = (
                [institution.short_name for institution in self.institutions.all()]
                + ["".join(["project:", slugify(project.acronym)]) for project in self.projects.all()]
                + [f"{speaker.first_name} {speaker.last_name}" for speaker in self.speakers.all()]
                + ([f"{self.main_speaker.first_name} {self.main_speaker.last_name}"] if self.main_speaker else [])
            )
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["event"]),
        ]
        ordering = ["start_at", "session_type__position", "room__position", "end_at"]

    def get_absolute_url(self) -> str:
        return "".join([self.event.get_absolute_url(), f"#/program/sessions/{self.id}/"])
