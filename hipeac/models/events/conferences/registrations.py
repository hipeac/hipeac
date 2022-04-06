from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..registrations import Registration, registration_post_save


class Fee:
    REGULAR = "regular"
    STUDENT = "student"


class ConferenceRegistration(Registration):
    fee_type = models.CharField(
        max_length=8, default=Fee.REGULAR, choices=((Fee.REGULAR, "Regular"), (Fee.STUDENT, "Student"))
    )
    with_booth = models.BooleanField(default=False)

    class Meta:
        db_table = "hipeac_conference_registration"
        verbose_name = "Conference registration"

    def save(self, *args, **kwargs):
        """
        `base_fee` is only calculated when the registration is created.
        `extra_fees` are recalculated every time.
        """
        is_early = self.is_early() if self.pk else self.event.is_early()

        if self.fee_type == Fee.STUDENT:
            base_fee = self.event.conference.early_student_fee if is_early else self.event.conference.student_fee
        else:
            base_fee = self.event.conference.early_fee if is_early else self.event.conference.fee

        self.base_fee = base_fee
        self.extra_fees = self.event.conference.booth_fee if self.with_booth else 0
        self.saldo = -self.remaining_fee
        super().save(*args, **kwargs)

    def is_early(self) -> bool:
        if not self.event.registration_early_deadline:
            return False
        return self.created_at <= self.event.registration_early_deadline


@receiver(post_save, sender=ConferenceRegistration)
def conference_registration_post_save(sender, instance, created, *args, **kwargs):
    registration_post_save(sender, instance, created, *args, **kwargs)
