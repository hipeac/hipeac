from django.contrib import admin
from django.utils.safestring import mark_safe

from hipeac.models import Article, Clipping, Quote
from .generic import ImagesInline


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    date_hierarchy = 'publication_date'
    inlines = (ImagesInline,)
    list_display = ('id', 'title', 'type', 'publication_date', 'is_ready')
    list_filter = ('type', 'publication_date')
    raw_id_fields = ['institutions', 'projects']
    search_fields = ['title']


@admin.register(Clipping)
class ClippingAdmin(admin.ModelAdmin):
    date_hierarchy = 'publication_date'
    list_display = ('id', 'title', 'publication_date', 'external_link')
    list_filter = ('publication_date',)
    search_fields = ['title', 'media']

    def external_link(self, obj):
        return mark_safe(f'<a target="_blank" href="{obj.url}">{obj.media}</a>')


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'author', 'type', 'is_featured')
    list_filter = ('type', 'is_featured')
    raw_id_fields = ['institution', 'user']
