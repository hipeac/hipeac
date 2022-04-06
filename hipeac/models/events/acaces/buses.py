from django.db import models


class AcacesBus(models.Model):
    DESTINATION_HOME = "home"
    DESTINATION_SCHOOL = "acaces"
    DESTINATION_CHOICES = (
        (DESTINATION_HOME, "Back home"),
        (DESTINATION_SCHOOL, "Summer School"),
    )

    event = models.ForeignKey("hipeac.Acaces", related_name="buses", on_delete=models.CASCADE)
    destination = models.CharField(max_length=8, choices=DESTINATION_CHOICES, default=DESTINATION_SCHOOL)
    name = models.CharField(max_length=128)
    position = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "hipeac_acaces_bus"
        ordering = ("event", "destination", "position")
        verbose_name = "ACACES bus"
        verbose_name_plural = "ACACES buses"

    def __str__(self) -> str:
        return self.name
