from django.contrib.postgres.fields import ArrayField
from django.db import models


class Email(models.Model):
    code = models.CharField(max_length=64, unique=True)
    action_name = models.CharField(max_length=128, help_text="This text is shown on the admin area dropdowns.")
    position = models.PositiveSmallIntegerField(default=0)
    from_email = models.CharField(
        "from",
        help_text="It can be a `Full Name &lt;email@domain.com&gt;` string or just an email address.",
        max_length=128,
    )
    cc_emails = ArrayField(models.EmailField(), default=list, blank=True, verbose_name="cc")
    reply_to_email = models.EmailField("reply-to", null=True)
    subject = models.CharField(max_length=255)
    template = models.TextField()

    def __str__(self) -> str:
        return self.code
