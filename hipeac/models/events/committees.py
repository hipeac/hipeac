from django.contrib.auth import get_user_model
from django.db import models


class Committee(models.Model):
    event = models.ForeignKey('hipeac.Event', related_name='committees', on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    members = models.ManyToManyField(get_user_model(), related_name='committees')
    position = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'hipeac_event_committee'
        ordering = ('position',)
