import uuid

from django.db import models


class PublicityEmail(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    msgid = models.CharField(max_length=1000, null=True, blank=True)
    date = models.CharField(max_length=100, null=True, blank=True)
    subject = models.TextField()
    content = models.TextField()
    content_type = models.CharField(max_length=190, null=True, blank=True)
    from_addresses = models.TextField(null=True, blank=True)
    to_addresses = models.TextField(null=True, blank=True)
    spam_level = models.PositiveSmallIntegerField(default=0)
    keywords = models.TextField(null=True, blank=True, editable=False)

    class Meta:
        db_table = "hipeac_publicity_email"
