import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from hashlib import sha256

from hipeac.functions import send_task
from .events import Event


class RegistrationAbstractModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), related_name="%(class)s_registrations", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["uuid"])]
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return str(self.uuid)


class Registration(RegistrationAbstractModel):
    event = models.ForeignKey("hipeac.Event", related_name="registrations", on_delete=models.CASCADE)

    base_fee = models.PositiveSmallIntegerField(default=0, editable=False)
    extra_fees = models.PositiveSmallIntegerField(default=0, editable=False)
    manual_extra_fees = models.PositiveSmallIntegerField(default=0)
    coupon = models.OneToOneField("hipeac.Coupon", null=True, blank=True, on_delete=models.SET_NULL)
    paid = models.PositiveSmallIntegerField("Paid online", default=0)
    paid_via_invoice = models.PositiveSmallIntegerField("Amount paid via invoice", default=0)
    saldo = models.IntegerField(default=0)

    invoice_requested = models.BooleanField(default=False)
    invoice_sent = models.BooleanField(default=False)
    visa_requested = models.BooleanField(default=False)
    visa_sent = models.BooleanField(default=False)

    sessions = models.ManyToManyField("hipeac.Session", related_name="registrations", blank=True)

    class Meta:
        db_table = "hipeac_event_registration"
        ordering = ("-id",)
        unique_together = ("event", "user")

    def __str__(self) -> str:
        return str(self.uuid)

    def get_email_class(self):
        from hipeac.emails.events import RegistrationEmail

        return RegistrationEmail

    def can_be_managed_by(self, user) -> bool:
        return self.user_id == user.id

    def editable_by_user(self, user) -> bool:
        return self.can_be_managed_by(user)

    def get_absolute_url(self) -> str:
        return "".join([self.event.get_absolute_url(), "#/registration/"])

    def get_payment_url(self) -> str:
        return reverse("registration_payment:payment", args=[self.id])

    def get_payment_result_url(self) -> str:
        return reverse("registration_payment:payment_result", args=[self.id])

    def get_payment_delegated_url(self) -> str:
        return reverse("registration_payment:payment_delegated", args=[self.uuid, self.secret])

    def get_payment_delegated_result_url(self) -> str:
        return reverse("registration_payment:payment_delegated_result", args=[self.uuid, self.secret])

    def get_receipt_url(self) -> str:
        return reverse("registration_payment:receipt", args=[self.id])

    @property
    def is_paid(self) -> bool:
        return self.saldo >= 0

    @property
    def remaining_fee(self):
        coupon_discount = self.coupon.value if self.coupon else 0
        return self.total_fee - self.paid - self.paid_via_invoice - coupon_discount

    @property
    def secret(self) -> str:
        return sha256(f"{self.uuid}{settings.SECRET_KEY}".encode("utf-8")).hexdigest()

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

        template, rt, from_email = "events.registrations.created", "registration", "management@hipeac.net"
        if event.type == Event.ACACES:
            template, rt, from_email = "events.registrations.created_acaces", "application", "acaces@hipeac.net"

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


@receiver(m2m_changed, sender=Registration.sessions.through)
def registration_sessions_changed(sender, instance, **kwargs) -> None:
    if kwargs.get("action") == "post_add":
        logs = list(RegistrationLog.objects.filter(registration_id=instance.id).values_list("session_id", flat=True))
        new_logs = []

        for session in instance.sessions.exclude(id__in=logs).only("id", "zoom_webinar_id"):
            new_logs.append(RegistrationLog(registration_id=instance.id, session_id=session.id))

            """
            if session.zoom_webinar_id:
                user = get_user_model().objects.select_related("profile").get(id=instance.user_id)
                send_task(
                    "hipeac.tasks.events.add_webinar_registrant",
                    (
                        (
                            session.id,
                            user.id,
                            session.zoom_webinar_int,
                            {
                                "email": user.email,
                                "first_name": user.first_name,
                                "last_name": user.last_name,
                                "country": user.profile.country.code,
                            },
                        ),
                    ),
                )
            """

        if new_logs:
            RegistrationLog.objects.bulk_create(new_logs)


class RegistrationLog(models.Model):
    """
    In some occasions, it can be interesting to know when somebody first registered for an activity.
    If later an activity is unselected, this log shows when the initial registration was made.
    """

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name="logs")
    session = models.ForeignKey("hipeac.Session", null=True, blank=True, on_delete=models.CASCADE, related_name="logs")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hipeac_event_registration_log"
        unique_together = ("registration", "session")
