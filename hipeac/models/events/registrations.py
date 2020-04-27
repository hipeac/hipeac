import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.urls import reverse

from hipeac.functions import send_task
from .fees import Fee


class Coupon(models.Model):
    """
    Coupons are used to pay or reduce registration fees.
    """

    code = models.UUIDField(default=uuid.uuid4, editable=False)
    event = models.ForeignKey("hipeac.Event", on_delete=models.CASCADE, related_name="coupons")
    value = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)])
    notes = models.CharField(max_length=190, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
        ]
        ordering = ["event", "id"]

    def __str__(self) -> str:
        return f"{self.code} (EUR {self.value})"


class RegistrationManager(models.Manager):
    def with_profiles(self):
        return super().get_queryset().select_related("user__profile").order_by("user__first_name", "user__last_name")


class Registration(models.Model):
    """
    A conference registration for a User.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    event = models.ForeignKey("hipeac.Event", on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.CASCADE, related_name="registrations")
    sessions = models.ManyToManyField("hipeac.Session", related_name="registrations")
    with_booth = models.BooleanField(default=False)

    fee_type = models.CharField(
        max_length=8, default=Fee.REGULAR, choices=((Fee.REGULAR, "Regular"), (Fee.STUDENT, "Student"))
    )
    base_fee = models.PositiveSmallIntegerField(default=0, editable=False)
    extra_fees = models.PositiveSmallIntegerField(default=0, editable=False)
    manual_extra_fees = models.PositiveSmallIntegerField(default=0)
    paid = models.PositiveSmallIntegerField("Paid online", default=0)
    paid_via_invoice = models.PositiveSmallIntegerField("Amount paid via invoice", default=0)
    saldo = models.IntegerField(default=0)
    coupon = models.OneToOneField(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    invoice_requested = models.BooleanField(default=False)
    invoice_sent = models.BooleanField(default=False)

    visa_requested = models.BooleanField(default=False)
    visa_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RegistrationManager()

    class Meta:
        indexes = [
            models.Index(fields=["uuid"]),
        ]
        ordering = ("-created_at",)
        unique_together = ("event", "user")

    def save(self, *args, **kwargs):
        """
        `base_fee` is only calculated when the registration is created.
        `extra_fees` are recalculated every time.
        """
        is_early = self.is_early() if self.pk else self.event.is_early()
        if self.fee_type == Fee.STUDENT:
            fee_type = Fee.EARLY_STUDENT if is_early else Fee.LATE_STUDENT
        else:
            fee_type = Fee.EARLY if is_early else Fee.LATE

        self.base_fee = self.event.fees_dict[fee_type] if fee_type in self.event.fees_dict else 0
        self.extra_fees = self.event.fees_dict[Fee.BOOTH] if self.with_booth else 0
        self.saldo = -self.remaining_fee
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.uuid} ({self.user})"

    def can_be_managed_by(self, user) -> bool:
        return self.user_id == user.id

    def get_absolute_url(self) -> str:
        return "".join([self.event.get_absolute_url(), "#/registration/"])

    def get_payment_url(self) -> str:
        return reverse("registration_payment", args=[self.id])

    def get_payment_result_url(self) -> str:
        return reverse("registration_payment_result", args=[self.id])

    def get_receipt_url(self) -> str:
        return reverse("registration_receipt", args=[self.id])

    def is_early(self) -> bool:
        if not self.event.registration_early_deadline:
            return False
        return self.created_at <= self.event.registration_early_deadline

    @property
    def is_paid(self) -> bool:
        return self.saldo >= 0

    @property
    def remaining_fee(self):
        coupon_discount = self.coupon.value if self.coupon else 0
        return self.total_fee - self.paid - self.paid_via_invoice - coupon_discount

    @property
    def total_fee(self):
        return self.base_fee + self.extra_fees + self.manual_extra_fees


@receiver(post_save, sender=Registration)
def registration_post_save(sender, instance, created, *args, **kwargs):
    if created:
        event = instance.event
        event.registrations_count = event.registrations.count()
        event.save()

        from hipeac.tools.notifications.events import RegistrationPendingNotificator

        RegistrationPendingNotificator().deleteOne(user_id=instance.user_id, event_id=event.id)

        email = (
            "events.registrations.created",
            f"[HiPEAC] Your registration for #{instance.event.hashtag} / {instance.id}",
            "HiPEAC <management@hipeac.net>",
            [instance.user.email],
            {
                "event_city": instance.event.city,
                "event_hashtag": instance.event.hashtag,
                "event_name": instance.event.name,
                "registration_id": instance.id,
                "registration_url": instance.get_absolute_url(),
                "visa_requested": instance.visa_requested,
            },
        )
        send_task("hipeac.tasks.emails.send_from_template", email)


@receiver(m2m_changed, sender=Registration.sessions.through)
def registration_sessions_changed(sender, instance, **kwargs) -> None:
    if kwargs.get("action") == "post_add":
        logs = list(RegistrationLog.objects.filter(registration_id=instance.id).values_list("session_id", flat=True))
        new_logs = []

        for session in instance.sessions.exclude(id__in=logs).only("id"):
            new_logs.append(RegistrationLog(registration_id=instance.id, session_id=session.id))

        if new_logs:
            RegistrationLog.objects.bulk_create(new_logs)


class RegistrationLog(models.Model):
    """
    In some occasions, it can be interesting to know when somebody first registered for an activity.
    If later an activity is unselected, this log shows when the initial registration was made.
    """

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name="logs")
    session = models.ForeignKey("hipeac.Session", on_delete=models.CASCADE, related_name="logs")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("registration", "session")
