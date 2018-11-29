from django.db import models
from django.utils import timezone


class Clipping(models.Model):
    media = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    url = models.URLField()
    # file = models.FileField(upload_to=get_asset_path, null=True, blank=True)
    publication_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-publication_date']

    def __str__(self) -> str:
        return f'Clipping @ {self.media}: {self.title}'
