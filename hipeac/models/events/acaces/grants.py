from django.db import models
from django_countries.fields import CountryField


class AcacesGrant(models.Model):
    event = models.ForeignKey("hipeac.Acaces", related_name="grants", on_delete=models.CASCADE)
    country = CountryField(db_index=True)
    available_grants = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "hipeac_acaces_grant"
        ordering = ("event", "country")
        unique_together = ("event", "country")
        verbose_name = "ACACES grant"
