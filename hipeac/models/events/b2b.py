from django.contrib.auth import get_user_model
from django.db import models


class B2b(models.Model):
    event = models.ForeignKey('hipeac.Event', on_delete=models.CASCADE, related_name='b2b')
    date = models.DateField()
    start_at = models.TimeField(null=True, blank=True)
    end_at = models.TimeField(null=True, blank=True)
    room = models.ForeignKey('hipeac.Room', null=True, blank=True, on_delete=models.SET_NULL, related_name='b2b')

    updated_at = models.DateTimeField(auto_now=True)
    reserved_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='b2b_reservations')

    class Meta:
        db_table = 'hipeac_event_b2b'
        ordering = ['date', 'room', 'start_at']

    def __str__(self) -> str:
        return f"{self.event} - B2B - {self.start_at}-{self.end_at}"
