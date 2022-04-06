from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..events import Event, event_post_save


class Conference(Event):
    fee = models.PositiveIntegerField(default=0)
    early_fee = models.PositiveIntegerField(default=0)
    student_fee = models.PositiveIntegerField(default=0)
    early_student_fee = models.PositiveIntegerField(default=0)
    booth_fee = models.PositiveIntegerField(default=0)

    def __init__(self, *args, **kwargs):
        self._meta.get_field("type").default = Event.CONFERENCE
        super().__init__(*args, **kwargs)


@receiver(post_save, sender=Conference)
def conference_post_save(sender, instance, created, *args, **kwargs):
    event_post_save(sender, instance, created, *args, **kwargs)
