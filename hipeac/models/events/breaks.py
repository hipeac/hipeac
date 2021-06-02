from django.db import models

from .events import validate_date


class Break(models.Model):
    COFFEE = "coffee"
    LUNCH = "lunch"
    TYPE_CHOICES = (
        (COFFEE, "Coffee break"),
        (LUNCH, "Lunch break"),
    )

    event = models.ForeignKey("hipeac.Event", related_name="breaks", on_delete=models.CASCADE)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=COFFEE)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "hipeac_event_break"
        ordering = ["start_at"]

    def clean(self) -> None:
        validate_date(self.start_at.date(), self.event)
