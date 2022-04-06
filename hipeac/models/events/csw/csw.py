from django.db.models.signals import post_save
from django.dispatch import receiver

from ..events import Event, event_post_save


class Csw(Event):
    class Meta:
        verbose_name = "CSW"

    def __init__(self, *args, **kwargs):
        self._meta.get_field("type").default = Event.CSW
        super().__init__(*args, **kwargs)


@receiver(post_save, sender=Csw)
def csw_post_save(sender, instance, created, *args, **kwargs):
    event_post_save(sender, instance, created, *args, **kwargs)
