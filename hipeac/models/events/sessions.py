import json

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


class Session(LinkMixin, models.Model):
    event = models.ForeignKey('hipeac.Event', on_delete=models.CASCADE, related_name='sessions')
    session_type = models.ForeignKey(Metadata, null=True, blank=False, on_delete=models.SET_NULL,
                                     limit_choices_to={'type': Metadata.SESSION_TYPE},
                                     related_name=Metadata.SESSION_TYPE)
    is_private = models.BooleanField(default=False)

    date = models.DateField()
    start_at = models.TimeField(null=True, blank=True)
    end_at = models.TimeField(null=True, blank=True)
    title = models.CharField(max_length=250)
    organizers = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    program = models.TextField(null=True, blank=True)
    main_speaker = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='talks')

    room = models.ForeignKey('hipeac.Room', null=True, blank=True, on_delete=models.SET_NULL, related_name='sessions')
    max_attendees = models.PositiveSmallIntegerField(default=0, help_text='Leave on `0` for non limiting.')
    extra_attendees_fee = models.PositiveSmallIntegerField(default=0)

    application_areas = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    acl = GenericRelation('hipeac.Permission')
    projects = models.ManyToManyField('hipeac.Project', blank=True, related_name='sessions')
    institutions = models.ManyToManyField('hipeac.Institution', blank=True, related_name='sessions')
    links = GenericRelation('hipeac.Link')
    private_files = GenericRelation('hipeac.PrivateFile')

    keywords = models.TextField(default='[]', editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.id:
            self.keywords = json.dumps(
                [institution.short_name for institution in self.institutions.all()] +
                [project.acronym for project in self.projects.all()] +
                ([self.main_speaker.first_name, self.main_speaker.last_name] if self.main_speaker else [])
            )
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['event', 'date']),
        ]
        ordering = ['date', 'start_at', 'room__position', 'end_at']

    def clean(self) -> None:
        validate_date(self.date, self.event)

    def __str__(self) -> str:
        return self.title

    def can_be_managed_by(self, user) -> bool:
        return (
            self.main_speaker_id == user.id or
            self.acl.filter(user_id=user.id, level__gte=Permission.ADMIN).exists()
        )

    def get_absolute_url(self) -> str:
        return ''.join([self.event.get_absolute_url(), f'#/schedule/sessions/{self.id}/'])

    def get_editor_url(self) -> str:
        content_type = ContentType.objects.get_for_model(self)
        return reverse('editor', args=[content_type.id, self.id])

    @property
    def is_industrial_session(self) -> bool:
        return self.session_type.value == 'Industrial Session'

    @property
    def slug(self) -> str:
        return slugify(self.title)
