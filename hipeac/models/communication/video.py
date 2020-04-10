from django.contrib.auth import get_user_model
from django.core.validators import validate_comma_separated_integer_list
from django.db import models

from .vars import SECTION_CHOICES


class Video(models.Model):
    type = models.CharField(max_length=16, null=True, blank=True, choices=SECTION_CHOICES)
    title = models.CharField(max_length=250)
    publication_date = models.DateField()
    youtube_id = models.CharField(max_length=40, unique=True)
    is_expert = models.BooleanField(default=True)

    application_areas = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    event = models.ForeignKey('hipeac.Event', null=True, blank=True, on_delete=models.SET_NULL, related_name='videos')
    users = models.ManyToManyField(get_user_model(), blank=True, related_name='videos')
    projects = models.ManyToManyField('hipeac.Project', blank=True, related_name='videos')

    class Meta:
        ordering = ['-publication_date']

    def __str__(self) -> str:
        return self.title
