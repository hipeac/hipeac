from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .buses import AcacesBus
from ..registrations import Registration, registration_post_save


class AcacesRegistration(Registration):
    STATUS_PENDING = 0  # 'u'
    STATUS_ADMITTED = 1  # 'a'
    STATUS_WAITING = 5  # 'w'
    STATUS_REJECTED = 9  # 'r'
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_ADMITTED, "Admitted"),
        (STATUS_WAITING, "In waiting list"),
        (STATUS_REJECTED, "Rejected"),
    )

    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    accepted = models.BooleanField("accepted by user", null=True)
    custom_data = models.JSONField(default=dict, blank=True, help_text="It can be used to update user's profile.")

    history = ArrayField(models.IntegerField(), default=list, blank=True)
    motivation = models.TextField(null=True, blank=True)
    courses = models.ManyToManyField("hipeac.AcacesCourse", related_name="registrations", blank=True)
    grant_requested = models.BooleanField(default=False)
    grant_assigned = models.BooleanField(null=True)
    assigned_hotel = models.ForeignKey(
        "hipeac.AcacesHotel", related_name="registrations", on_delete=models.SET_NULL, null=True, blank=True
    )

    roommate_requested = models.BooleanField(default=False)
    roommate_notes = models.CharField(max_length=190, null=True, blank=True)
    roommate = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)

    arrival_flight = models.CharField(max_length=190, null=True, blank=True)
    arrival_bus = models.ForeignKey(
        "hipeac.AcacesBus",
        related_name="registrations_arriving",
        limit_choices_to={"destination": AcacesBus.DESTINATION_SCHOOL},
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    departure_bus = models.ForeignKey(
        "hipeac.AcacesBus",
        related_name="registrations_departing",
        limit_choices_to={"destination": AcacesBus.DESTINATION_HOME},
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    departure_flight = models.CharField(max_length=190, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    gelato = models.BooleanField(default=False, editable=False)

    class Meta:
        db_table = "hipeac_acaces_registration"
        verbose_name = "ACACES registration"

    def save(self, *args, **kwargs):
        """
        `base_fee` is only calculated when the registration is created.
        `extra_fees` are recalculated every time.
        """
        if self.roommate:
            base_fee = self.event.acaces.fee - self.event.acaces.shared_room_discount
            if self.roommate.grant_assigned:
                base_fee = base_fee - self.event.acaces.shared_room_discount
        else:
            base_fee = self.event.acaces.fee

        if self.status != self.STATUS_ADMITTED or self.grant_assigned or self.accepted is False:
            base_fee = 0

        self.base_fee = base_fee
        self.saldo = -self.remaining_fee
        super().save(*args, **kwargs)


@receiver(post_save, sender=AcacesRegistration)
def acaces_registration_post_save(sender, instance, created, *args, **kwargs):
    registration_post_save(sender, instance, created, *args, **kwargs)
