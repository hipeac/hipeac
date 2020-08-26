from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import validate_comma_separated_integer_list
from django.db import models

from ..communication import Video
from .events import validate_date


class Course(models.Model):
    event = models.ForeignKey("hipeac.Event", related_name="courses", on_delete=models.CASCADE)
    title = models.CharField(max_length=250, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    teachers = models.ManyToManyField(get_user_model(), blank=True, related_name="courses")
    topics = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])

    links = GenericRelation("hipeac.Link")
    private_files = GenericRelation("hipeac.PrivateFile")

    class Meta:
        db_table = "hipeac_event_course"

    def __str__(self) -> str:
        return f"{self.title}"

    @property
    def hours(self) -> float:
        return round(self.minutes / 60, 1)

    @property
    def minutes(self) -> int:
        return sum([s.minutes for s in self.sessions.all()])

    @property
    def teachers_string(self) -> str:
        return " / ".join([t.profile.name for t in self.teachers.all()])

    @property
    def videos(self):
        teacher_id = self.teachers.all()[0].id
        return Video.objects.filter(event_id=self.event_id, users__pk=teacher_id)


class CourseSession(models.Model):
    course = models.ForeignKey(Course, related_name="sessions", on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    notes = models.TextField(null=True, blank=True)
    zoom_attendee_report = models.FileField(upload_to="private/zoom", null=True, blank=True)

    links = GenericRelation("hipeac.Link")

    class Meta:
        db_table = "hipeac_event_course_session"
        ordering = ["start_at"]

    def clean(self) -> None:
        validate_date(self.start_at.date(), self.course.event)
        if self.start_at.date() != self.end_at.date():
            raise ValidationError("Start and end date must be the same.")

    def __str__(self) -> str:
        return f"{self.course} ({self.start_at.date()})"

    @property
    def minutes(self) -> int:
        return int((self.end_at - self.start_at).total_seconds() / 60.0)
