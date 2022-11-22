from django.contrib.auth import get_user_model
from django.db import models

from ..projects import Project


class Hipeac(Project):
    """
    A HiPEAC project.
    """

    class Meta:
        db_table = "hipeac_self"


class HipeacPartner(models.Model):
    """
    A HiPEAC partner.
    """

    hipeac = models.ForeignKey(Hipeac, on_delete=models.CASCADE, related_name="partners")
    institution = models.ForeignKey("hipeac.Institution", null=True, blank=False, on_delete=models.SET_NULL)
    description = models.TextField(null=True, blank=True)
    representative = models.ForeignKey(
        get_user_model(), related_name="as_representative", null=True, blank=False, on_delete=models.SET_NULL
    )
    position = models.PositiveSmallIntegerField(default=0)
    tasks = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = "hipeac_self_partner"
        ordering = ("hipeac", "position")
