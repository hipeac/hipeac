from django.contrib.auth import get_user_model
from django.db import models


class Hipeac(models.Model):
    """
    HiPEAC project.
    """
    project = models.ForeignKey('hipeac.Project', null=True, blank=False, on_delete=models.SET_NULL)
    visible = models.BooleanField(default=False)


class HipeacPartner(models.Model):
    hipeac = models.ForeignKey('hipeac.HiPEAC', on_delete=models.CASCADE, related_name='partners')
    institution = models.ForeignKey('hipeac.Institution', null=True, blank=False, on_delete=models.SET_NULL)
    description = models.TextField(null=True, blank=True)
    representative = models.ForeignKey(get_user_model(), related_name='as_representative', null=True, blank=False,
                                       on_delete=models.SET_NULL)
    position = models.PositiveSmallIntegerField(default=0)
    tasks = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        ordering = ['hipeac', 'position']
