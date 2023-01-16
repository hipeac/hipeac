from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify

from hipeac.models.mixins import (
    ApplicationAreasMixin,
    EditorMixin,
    FilesMixin,
    InstitutionsMixin,
    KeywordsMixin,
    LinksMixin,
    PermissionsMixin,
    ProjectsMixin,
    TopicsMixin,
    UsersMixin,
    VideosMixin,
)
from .events import validate_date
from ..metadata import Metadata
from ..permissions import Permission


class SessionManager(models.Manager):
    def all(self):
        return (
            super()
            .get_queryset()
            .select_related("type")
            .prefetch_related(
                "files",
                "links",
                "main_speaker__profile__institution",
                "rel_application_areas__application_area",
                "rel_institutions__institution",
                "rel_projects__project",
                "rel_topics__topic",
                "rel_users__user__profile",
                "rel_videos__video",
            )
        )


class SessionAbstractBaseModel(PermissionsMixin, models.Model):
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    max_attendees = models.PositiveSmallIntegerField(default=0, help_text="Leave on `0` for non limiting.")
    zoom_webinar_id = models.CharField(max_length=32, null=True, blank=True)
    zoom_attendee_report = models.FileField(upload_to="private/zoom", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def zoom_webinar_int(self) -> int:
        return int(self.zoom_webinar_id.replace(" ", ""))


class SessionAbstractModel(
    SessionAbstractBaseModel,
    ApplicationAreasMixin,
    FilesMixin,
    InstitutionsMixin,
    KeywordsMixin,
    LinksMixin,
    ProjectsMixin,
    TopicsMixin,
    UsersMixin,
    VideosMixin,
):
    is_private = models.BooleanField(default=False)
    type = models.ForeignKey(
        Metadata,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        limit_choices_to={"type": Metadata.SESSION_TYPE},
    )
    main_speaker = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    title = models.CharField(max_length=250)
    organizers = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    program = models.TextField(null=True, blank=True)

    # objects = SessionManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.id:
            self.keywords = (
                [institution.short_name for institution in self.institutions]
                + ["".join(["project:", slugify(project.acronym)]) for project in self.projects]
                + [f"{speaker.first_name} {speaker.last_name}" for speaker in self.users]
                + ([f"{self.main_speaker.first_name} {self.main_speaker.last_name}"] if self.main_speaker else [])
            )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        date = self.start_at.strftime("%a %-H:%M")
        return f"{date}: {self.title}"


class Session(EditorMixin, SessionAbstractModel):
    event = models.ForeignKey("hipeac.Event", related_name="sessions", on_delete=models.CASCADE)
    room = models.ForeignKey("hipeac.Room", null=True, blank=True, on_delete=models.SET_NULL)
    extra_attendees_fee = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "hipeac_event_session"
        ordering = ("start_at",)

    def clean(self) -> None:
        validate_date(self.start_at.date(), self.event)

    def get_email_class(self):
        from hipeac.emails.events import SessionEmail

        return SessionEmail

    def can_be_managed_by(self, user) -> bool:
        return self.main_speaker_id == user.id or self._can_be_managed_by(user)

    def get_absolute_url(self) -> str:
        return "".join([self.event.get_absolute_url(), f"#/program/sessions/{self.id}/"])

    @property
    def slug(self) -> str:
        return slugify(self.title)


class SessionAccessLink(models.Model):
    session = models.ForeignKey("hipeac.Session", on_delete=models.CASCADE, related_name="access_links")
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.CASCADE, related_name="access_links")
    url = models.URLField(max_length=500)

    class Meta:
        db_table = "hipeac_event_session_link"
