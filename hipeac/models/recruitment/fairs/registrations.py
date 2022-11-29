import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from hipeac.functions import send_task


class JobFairRegistration(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), related_name="job_fair_registrations", on_delete=models.CASCADE)
    fair = models.ForeignKey("hipeac.JobFair", related_name="registrations", on_delete=models.CASCADE)

    jobs = models.ManyToManyField("hipeac.Job", related_name="jobs", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hipeac_job_fair_registration"
        ordering = ("-id",)
        unique_together = ("fair", "user")

    def __str__(self) -> str:
        return str(self.uuid)

    def can_be_managed_by(self, user) -> bool:
        return self.user_id == user.id


@receiver(post_save, sender=JobFairRegistration)
def jobfairregistration_post_save(sender, instance, created, *args, **kwargs):
    if created:
        """
        send email?
        """
        """
        template, rt, from_email = "events.registrations.created", "registration", "management@hipeac.net"

        email = (
            template,
            f"[HiPEAC] Your {rt} for #{instance.event.hashtag} / {instance.id}",
            f"HiPEAC <{from_email}>",
            [instance.user.email],
            {
                "event_city": instance.event.city,
                "event_hashtag": instance.event.hashtag,
                "event_name": instance.event.name,
                "registration_id": instance.id,
                "registration_url": instance.get_absolute_url(),
                "user_name": instance.user.profile.name,
                "visa_requested": instance.visa_requested,
            },
        )
        send_task("hipeac.tasks.emails.send_from_template", email)
        """
        pass
