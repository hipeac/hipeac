from django.db import models
from django.utils import timezone


class Vision(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    publication_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-publication_date']
