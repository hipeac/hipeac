import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from hipeac.functions import send_task
from hipeac.site.emails.events.events import SessionProposalEmail
from ...mixins import ApplicationAreasMixin, TopicsMixin


class WebinarProposal(ApplicationAreasMixin, TopicsMixin, models.Model):
    """
    A session proposal for a conference.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField()

    title = models.CharField(max_length=250)
    organizers = models.TextField()
    summary = models.TextField()
    projects = models.TextField(null=True, blank=True)
    duration = models.CharField(max_length=250)
    session_format = models.CharField(max_length=250, null=True, blank=True)
    expected_attendees = models.CharField(max_length=250)
    previous_editions = models.TextField(null=True, blank=True)
    other = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hipeac_webinar_proposal"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("webinar_proposal_update", args=[self.uuid])


@receiver(post_save, sender=WebinarProposal)
def session_proposal_post_save(sender, instance, created, *args, **kwargs):
    from hipeac.emails.webinars import WebinarProposalEmail

    WebinarProposalEmail("events.webinars.proposal", instance).send()
