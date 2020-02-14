import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField

from hipeac.functions import send_task
from hipeac.site.emails.events import OpenRegistrationCreatedEmail


class OpenRegistration(models.Model):
    """
    A session proposal for a conference.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    event = models.ForeignKey('hipeac.OpenEvent', on_delete=models.CASCADE, related_name='registrations')

    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField()
    affiliation = models.CharField(max_length=250)
    address = models.CharField(max_length=250, null=True, blank=True)
    zip_code = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country_raw = models.CharField(max_length=250, null=True, blank=True)
    country = CountryField(null=True, blank=True)

    visa_requested = models.BooleanField(default=False)
    visa_sent = models.BooleanField(default=False)

    fields = models.TextField(default='{}')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self) -> str:
        return f"{self.event.custom_url}#/r/{self.uuid}/"


@receiver(post_save, sender=OpenRegistration)
def open_registration_post_save(sender, instance, created, *args, **kwargs):
    if created:
        event = instance.event
        event.registrations_count = event.registrations.count()
        event.save()

        email = OpenRegistrationCreatedEmail(instance=instance)
        send_task('hipeac.tasks.emails.send_from_template', email.data)
