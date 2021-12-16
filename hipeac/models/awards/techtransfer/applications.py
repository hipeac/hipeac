from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from hipeac.functions import send_task
from hipeac.site.emails.awards import TechTransferApplicationEmail


class TechTransferApplication(models.Model):
    """
    A technology transfer example eligible for a Technology Transfer Award.
    """

    call = models.ForeignKey("hipeac.TechTransferCall", related_name="applications", on_delete=models.CASCADE)
    applicant = models.ForeignKey(
        "auth.User", related_name="technology_transfer_award_applications", null=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=250)
    description = models.TextField("Description of the technology being transferred")
    partners_description = models.TextField("Description of the academic partners and the company involved")
    value = models.TextField("Estimate of the value of the agreement")
    team = models.ManyToManyField(
        "auth.User",
        blank=True,
        related_name="technology_transfer_awards",
        help_text="Team members that will receive an award (certificate).",
    )

    team_string = models.TextField("Team (text)", null=True, blank=True)

    awarded = models.BooleanField(default=None, null=True)
    awardee = models.OneToOneField(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="technology_transfer_financial_award",
    )
    awarded_summary = models.TextField("Summary", null=True, help_text="Summary, if awarded, to show online.")
    awarded_from = models.ForeignKey(
        "hipeac.Institution", related_name="ttawards_from", null=True, blank=True, on_delete=models.SET_NULL
    )
    awarded_to = models.ForeignKey(
        "hipeac.Institution", related_name="ttawards_to", null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def clean(self):
        """
        Validates the model before saving.
        """
        if self.call.is_frozen:
            raise ValidationError('Call is "frozen": no more changes are allowed in applications.')
        if self.awardee and not self.awarded:
            raise ValidationError("Please check that the `awarded` field has been updated.")

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("techtransfer_update", args=[self.id])


@receiver(post_save, sender=TechTransferApplication)
def session_proposal_post_save(sender, instance, created, *args, **kwargs):
    if created:
        email = TechTransferApplicationEmail(instance=instance)
        send_task("hipeac.tasks.emails.send_from_template", email.data)
