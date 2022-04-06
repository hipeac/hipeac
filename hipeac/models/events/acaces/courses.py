from django.db import models

from hipeac.models.mixins import (
    ApplicationAreasMixin,
    FilesMixin,
    LinksMixin,
    ProjectsMixin,
    TopicsMixin,
    UsersMixin,
    VideosMixin,
)
from ..sessions import SessionAbstractBaseModel


class AcacesCourseManager(models.Manager):
    def all(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "files",
                "links",
                "rel_application_areas__application_area",
                "rel_projects__project",
                "rel_topics__topic",
                "rel_users__user__profile",
                "rel_videos__video",
            )
        )


class AcacesCourse(
    ApplicationAreasMixin, FilesMixin, LinksMixin, ProjectsMixin, TopicsMixin, UsersMixin, VideosMixin, models.Model
):
    event = models.ForeignKey("hipeac.Acaces", related_name="courses", on_delete=models.CASCADE)
    slot = models.PositiveSmallIntegerField(null=True, blank=True)
    title = models.CharField(max_length=250)
    overview = models.TextField(null=True, blank=True)

    # objects = AcacesCourseManager()

    class Meta:
        db_table = "hipeac_acaces_course"
        ordering = ("event", "slot", "title")
        verbose_name = "ACACES course"

    def __str__(self) -> str:
        slot = f"Slot {self.slot}: " if self.slot else ""
        return f"{slot}{self.title}"

    @property
    def hours(self) -> float:
        return round(self.minutes / 60, 1)

    @property
    def minutes(self) -> int:
        return sum([s.minutes for s in self.sessions.all()])

    @property
    def teachers(self):
        return self.users


class AcacesCourseSession(SessionAbstractBaseModel):
    course = models.ForeignKey(AcacesCourse, related_name="sessions", on_delete=models.CASCADE)
    overview = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "hipeac_acaces_course_session"
        ordering = ("course", "start_at")

    def __str__(self) -> str:
        return f"#{self.id}"

    @property
    def minutes(self) -> int:
        return int((self.end_at - self.start_at).total_seconds() / 60.0)
