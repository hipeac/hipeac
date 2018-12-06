from django.contrib import admin
from django.forms import ModelForm
from django.utils.safestring import mark_safe

from hipeac.forms import ApplicationAreasChoiceField, TopicsChoiceField
from hipeac.models.communication import Article, Clipping, Magazine, Quote, Video
from .generic import ImagesInline


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    date_hierarchy = 'publication_date'
    list_display = ('id', 'title', 'type', 'publication_date', 'is_ready')
    list_filter = ('type', 'publication_date')
    search_fields = ('title',)

    autocomplete_fields = ('event', 'institutions', 'projects')
    radio_fields = {'type': admin.VERTICAL}
    readonly_fields = ('created_by',)
    inlines = (ImagesInline,)


@admin.register(Clipping)
class ClippingAdmin(admin.ModelAdmin):
    date_hierarchy = 'publication_date'
    list_display = ('id', 'title', 'publication_date', 'external_link')
    list_filter = ('publication_date',)
    search_fields = ('title', 'media')

    def external_link(self, obj):
        return mark_safe(f'<a target="_blank" href="{obj.url}">{obj.media}</a>')


class MagazineAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField(required=False)
    topics = TopicsChoiceField(required=False)


@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    form = MagazineAdminForm

    date_hierarchy = 'publication_date'
    list_display = ('id', 'title', 'publication_date')

    autocomplete_fields = ('users', 'projects')
    fieldsets = (
        (None, {
            'fields': ('title', 'publication_date', 'issuu_url', 'file', 'file_tablet',),
        }),
        ('RELATIONS', {
            'classes': ('collapse',),
            'fields': ('users', 'projects'),
        }),
        ('METADATA', {
            'classes': ('collapse',),
            'fields': ('application_areas', 'topics'),
        }),
    )


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'author', 'type', 'is_featured')
    list_filter = ('type', 'is_featured')

    autocomplete_fields = ('institution', 'user')


class VideoAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField(required=False)
    topics = TopicsChoiceField(required=False)

    class Meta:
        help_texts = {
            'is_expert': 'If checked, the video will be shown on the press area.',
        }


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    form = VideoAdminForm

    date_hierarchy = 'publication_date'
    list_display = ('id', 'title', 'publication_date', 'youtube_id', 'is_expert')
    list_filter = ('is_expert',)
    search_fields = ('title',)

    raw_id_fields = ('user', 'project')
    fieldsets = (
        (None, {
            'fields': ('title', 'publication_date', 'youtube_id', 'is_expert'),
        }),
        ('RELATIONS', {
            'classes': ('collapse',),
            'fields': ('user', 'project'),
        }),
        ('METADATA', {
            'classes': ('collapse',),
            'fields': ('application_areas', 'topics'),
        }),
    )
