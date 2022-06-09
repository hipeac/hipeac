from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property

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

    @cached_property
    def jobs(self):
        from hipeac.models import Job

        sponsors = self.sponsors.values_list("institution_id", "project_id")
        a, b = map(list, zip(*sponsors))
        institution_ids, project_ids = list(filter(None, a)), list(filter(None, b))

        return (
            Job.objects.active()
            .filter(
                (
                    Q(institution__in=institution_ids)
                    | Q(project__in=project_ids)
                    | Q(institution__parent_id__in=institution_ids)
                ),
            )
            .order_by("institution__name", "deadline")
        )


@receiver(post_save, sender=Conference)
def conference_post_save(sender, instance, created, *args, **kwargs):
    event_post_save(sender, instance, created, *args, **kwargs)
