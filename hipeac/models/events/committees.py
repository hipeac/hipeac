from django.db import models

from ..mixins import UsersMixin


class CommitteeManager(models.Manager):
    def all(self):
        return super().get_queryset().prefetch_related("rel_users__user__profile")


class Committee(UsersMixin, models.Model):
    event = models.ForeignKey("hipeac.Event", related_name="committees", on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    position = models.PositiveSmallIntegerField()

    objects = CommitteeManager()

    class Meta:
        db_table = "hipeac_event_committee"
        ordering = ("position",)

    @property
    def members(self):
        return self.users
