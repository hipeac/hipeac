from django.db import models

from .events import validate_date


class Break(models.Model):
    COFFEE = 'coffee'
    LUNCH = 'lunch'
    TYPE_CHOICES = (
        (COFFEE, 'Coffee break'),
        (LUNCH, 'Lunch break'),
    )

    event = models.ForeignKey('hipeac.Event', related_name='breaks', on_delete=models.CASCADE)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=COFFEE)
    date = models.DateField()
    start_at = models.TimeField()
    end_at = models.TimeField()
    notes = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'hipeac_event_break'
        ordering = ['date', 'start_at']

    def clean(self) -> None:
        validate_date(self.date, self.event)
