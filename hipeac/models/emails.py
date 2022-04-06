from django.contrib.postgres.fields import ArrayField
from django.db import models


class Email(models.Model):
    code = models.CharField(max_length=64, unique=True)
    action_name = models.CharField(max_length=128, help_text="This text is shown on the admin area dropdowns.")
    position = models.PositiveSmallIntegerField(default=0)
    from_email = models.EmailField()
    extra_to_emails = ArrayField(models.EmailField(), default=list, editable=False, blank=True)
    subject = models.CharField(max_length=255)
    template = models.TextField()
