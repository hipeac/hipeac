from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse

from ..mixins import LinkMixin


class Meeting(LinkMixin, models.Model):
    """
    Steering Committee meeting.
    """
    ASSETS_PRIVATE_FOLDER = 'private/steering/meeting'

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    location = models.CharField(max_length=250)
    description = models.TextField()
    url_webex = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    file = models.FileField(upload_to=ASSETS_PRIVATE_FOLDER, null=True, blank=True)
    attachments = GenericRelation('hipeac.PrivateFile')

    class Meta:
        ordering = ['-start_at']

    def get_absolute_url(self) -> str:
        return ''.join([reverse('steering'), f'#/meetings/{self.id}/'])
