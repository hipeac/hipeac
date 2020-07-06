from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import validate_comma_separated_integer_list
from django.db import models

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


class CourseSession(models.Model):
    course = models.ForeignKey(Course, related_name="sessions", on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    notes = models.TextField(null=True, blank=True)
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
