from django.core.validators import MinValueValidator
from django.db import models


class Fee(models.Model):
    """
    Coupons are used to pay or reduce registration fees.
    """
    EARLY = 'early'
    LATE = 'late'
    EARLY_STUDENT = 'early_student'
    LATE_STUDENT = 'late_student'
    BOOTH = 'late_student'
    TYPE_CHOICES = (
        (EARLY, 'Early'),
        (LATE, 'Late'),
        (EARLY_STUDENT, 'Early (student)'),
        (LATE_STUDENT, 'Late (student)'),
        (BOOTH, 'Booth fee'),
    )

    event = models.ForeignKey('hipeac.Event', on_delete=models.CASCADE, related_name='fees')
    type = models.CharField(max_length=16, editable=False, choices=TYPE_CHOICES)
    value = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)])
    notes = models.CharField(max_length=190, null=True, blank=True)

    class Meta:
        db_table = 'hipeac_event_fee'

    def __str__(self) -> str:
        return '{0} ({1})'.format(self.type, self.value)
