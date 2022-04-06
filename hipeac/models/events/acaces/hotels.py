from django.db import models
from django.template.defaultfilters import slugify


class AcacesHotel(models.Model):
    event = models.ForeignKey("hipeac.Acaces", related_name="hotels", on_delete=models.CASCADE)
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=128)
    available_rooms = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "hipeac_acaces_hotel"
        verbose_name = "ACACES hotel"

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    def slug(self) -> str:
        return slugify(f"{self.code}-{self.name}")
