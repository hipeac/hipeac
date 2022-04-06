from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from hipeac.functions import send_task
from hipeac.site.emails.awards import TechTransferApplicationEmail
from ..mixins import UsersMixin


class TechTransferCallQuerySet(models.QuerySet):
    def active(self):
        today = timezone.now().date()
        return self.filter(start_date__lte=today, end_date__gte=today).first()


class TechTransferCall(models.Model):
    """
    A call for Technology Transfer Awards.
    """

    start_date = models.DateField()
    end_date = models.DateField()
    is_frozen = models.BooleanField(default=False, help_text="Check this box to avoid further editing on applications.")

    created_at = models.DateTimeField(auto_now_add=True)

    objects = TechTransferCallQuerySet.as_manager()

    class Meta:
        db_table = "hipeac_tech_transfer_call"
        ordering = ("-start_date",)

    def __str__(self) -> str:
        return self.start_date.strftime("%Y %b")

    def is_active(self) -> bool:
        return self.start_date <= timezone.now().date() <= self.end_date

    def is_closed(self) -> bool:
        return self.end_date < timezone.now().date()

    @property
    def year(self) -> int:
        return self.start_date.year


class TechTransferApplicationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("call", "award")


class TechTransferApplication(models.Model):
    """
    A technology transfer example eligible for a Technology Transfer Award.
    """

    call = models.ForeignKey("hipeac.TechTransferCall", related_name="applications", on_delete=models.CASCADE)
    applicant = models.ForeignKey(
        "auth.User", related_name="tech_transfer_applications", null=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=250)
    description = models.TextField("Description of the technology being transferred")
    partners_description = models.TextField("Description of the academic partners and the company involved")
    value = models.TextField("Estimate of the value of the agreement")
    team_string = models.TextField("Team (text)", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = TechTransferApplicationManager()

    class Meta:
        db_table = "hipeac_tech_transfer_application"
        ordering = ("-created_at",)

    def clean(self):
        """
        Validates the model before saving.
        """
        if self.call.is_frozen:
            raise ValidationError('Call is "frozen": no more changes are allowed in applications.')

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("tech_transfer_update", args=[self.id])

    @property
    def awarded(self) -> int:
        return self.award.exists()


@receiver(post_save, sender=TechTransferApplication)
def tech_transfer_application_post_save(sender, instance, created, *args, **kwargs):
    if created:
        email = TechTransferApplicationEmail(instance=instance)
        send_task("hipeac.tasks.emails.send_from_template", email.data)


class TechTransferAward(UsersMixin, models.Model):
    """
    A Technology Transfer Award.
    """

    application = models.OneToOneField("hipeac.TechTransferApplication", related_name="award", on_delete=models.CASCADE)
    awardee = models.OneToOneField(
        "auth.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="tech_transfer_award",
    )
    summary = models.TextField("Summary", help_text="Summary to show online.", null=True, blank=True)
    origin_institution = models.ForeignKey(
        "hipeac.Institution", related_name="originated_tech_transfers", null=True, on_delete=models.SET_NULL
    )
    recipient_institution = models.ForeignKey(
        "hipeac.Institution", related_name="received_tech_transfers", null=True, on_delete=models.SET_NULL
    )

    class Meta:
        db_table = "hipeac_tech_transfer_award"
