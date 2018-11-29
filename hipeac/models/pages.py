from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.flatpages.models import FlatPage
from django.db import models
from django.utils.functional import cached_property


class Page(FlatPage):
    def __str__(self) -> str:
        return self.url

    @cached_property
    def tbs(self):
        return {
            block.key: block for block in self.blocks.prefetch_related('images')
        }


class Block(models.Model):
    page = models.ForeignKey(Page, related_name='blocks', on_delete=models.CASCADE)
    key = models.CharField(max_length=32)
    notes = models.CharField(max_length=255, blank=True)
    header = models.TextField(blank=True)
    content = models.TextField()

    images = GenericRelation('hipeac.Image')

    class Meta:
        ordering = ['page', 'key']
        unique_together = ('page', 'key')
        verbose_name = 'page block'

    def __str__(self) -> str:
        return self.key
