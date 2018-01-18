from django.db import models
from django.utils.text import slugify
from typing import List


class Track(models.Model):
    event = models.ForeignKey('hipeac.Event', on_delete=models.CASCADE, related_name='tracks')
    name = models.CharField(max_length=64)

    class Meta:
        db_table = 'hipeac_event_track'

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def autocomplete_search_fields() -> List[str]:
        return ['name__icontains']

    @property
    def slug(self) -> str:
        return slugify(self.name)
