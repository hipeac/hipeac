from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from hipeac.models import Permission
from hipeac.tools.mailer import send_internal_email
from ..mixins import EditorMixin


class JobEvaluation(EditorMixin, models.Model):
    """
    A job evaluation.
    """

    NO = 0
    YES = 2
    YES_HIPEAC = 1
    VALUE_CHOICES = (
        (NO, "No"),
        (YES, "Yes"),
        (YES_HIPEAC, "Yes, via the HiPEAC Jobs portal!"),
    )

    job = models.OneToOneField("hipeac.Job", on_delete=models.CASCADE, related_name="evaluation")
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    comments = models.TextField(null=True, blank=True)
    selected_candidate = models.CharField(max_length=250, null=True, blank=True)
    selected_user = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="selected_jobs",
        help_text="Internal use only.",
    )

    class Meta:
        db_table = "hipeac_job_evaluation"

    def __str__(self) -> str:
        return self.job.title

    def can_be_managed_by(self, user) -> bool:
        return (
            self.job.created_by_id == user.id
            or self.job.institution.acl.filter(user_id=user.id, level__gte=Permission.ADMIN).exists()
        )


@receiver(post_save, sender=JobEvaluation)
def job_evaluation_post_save(sender, instance, created, *args, **kwargs):
    if created:
        send_internal_email(
            to="HiPEAC Recruitment <recruitment@hipeac.net>",
            subject=f"[HiPEAC] New job evaluation / #{instance.id}",
            template="_emails_internal/recruitment__evaluation_created.txt",
            context={"evaluation": instance},
        )
