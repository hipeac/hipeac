from django.db import models
from django.utils import timezone


class TechTransferCallManager(models.Manager):

    def active(self):
        today = timezone.now().date()
        return self.filter(start_date__lte=today, end_date__gte=today).first()


class TechTransferCall(models.Model):
    """
    A call for Technology Transfer Awards.
    """
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_frozen = models.BooleanField(default=False, help_text='Check this box to avoid further editing on applications.')

    objects = TechTransferCallManager()

    class Meta:
        ordering = ('-start_date',)

    def __str__(self) -> str:
        return self.start_date.strftime('%Y %b')

    def is_active(self) -> bool:
        return self.start_date <= timezone.now().date() <= self.end_date

    def is_closed(self) -> bool:
        return self.end_date < timezone.now().date()

    @property
    def year(self) -> int:
        return self.start_date.year
