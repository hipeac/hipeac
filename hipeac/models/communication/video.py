from django.contrib.auth import get_user_model
from django.core.validators import validate_comma_separated_integer_list
from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=250)
    publication_date = models.DateField()
    youtube_id = models.CharField(max_length=40)
    is_expert = models.BooleanField(default=True)
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL, related_name='videos')
    project = models.ForeignKey('hipeac.Project', null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='videos')

    application_areas = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])

    class Meta:
        ordering = ['-publication_date']

    def __str__(self) -> str:
        return self.title
