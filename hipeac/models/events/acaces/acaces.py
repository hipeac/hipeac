from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_countries import countries

from ..events import Event, event_post_save


class Acaces(Event):
    fee = models.PositiveIntegerField(default=0)
    shared_room_discount = models.PositiveIntegerField(default=0)
    grant_request_deadline = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "ACACES summer school"

    def __init__(self, *args, **kwargs):
        self._meta.get_field("type").default = Event.ACACES
        super().__init__(*args, **kwargs)

    def is_open_for_grants(self) -> bool:
        return timezone.now() < self.grant_request_deadline if self.grant_request_deadline else False

    @property
    def double_discount(self) -> int:
        return self.shared_room_discount * 2

    @property
    def fee_discounted(self) -> int:
        return self.fee - self.shared_room_discount

    @property
    def fee_double_discounted(self) -> int:
        return self.fee - self.double_discount


@receiver(post_save, sender=Acaces)
def acaces_post_save(sender, instance, created, *args, **kwargs):
    event_post_save(sender, instance, created, *args, **kwargs)

    if created:
        from .grants import AcacesGrant

        for code, name in list(countries):
            AcacesGrant(country=code, event_id=instance.id).save()
