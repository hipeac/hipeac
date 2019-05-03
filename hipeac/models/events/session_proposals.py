import uuid

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.urls import reverse


class SessionProposal(models.Model):
    """
    A session proposal for a conference.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    event = models.ForeignKey('hipeac.Event', on_delete=models.CASCADE, related_name='session_proposals')

    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField()

    title = models.CharField(max_length=250)
    organizers = models.TextField()
    summary = models.TextField()
    projects = models.TextField(null=True, blank=True)
    workshop_deadlines = models.TextField(null=True, blank=True)
    tutorial_biblio = models.TextField(null=True, blank=True)
    duration = models.CharField(max_length=250)
    session_format = models.CharField(max_length=250)
    expected_attendees = models.CharField(max_length=250)
    room_configuration = models.CharField(max_length=250)
    previous_editions = models.TextField(null=True, blank=True)
    other = models.TextField(null=True, blank=True)

    application_areas = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self) -> str:
        return reverse('session_proposal_update', args=[self.event_id, self.uuid])
