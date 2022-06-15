from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from django.utils.html import format_html

from hipeac.models.communication import (
    Article,
    Clipping,
    Dissemination,
    Magazine,
    MagazineRecipient,
    Quote,
    Video,
    RelatedVideo,
)
from .files import FilesInline
from .institutions import InstitutionsInline
from .images import ImagesInline
from .metadata import ApplicationAreasInline, TopicsInline
from .projects import ProjectsInline
from .users import UsersInline
from .widgets import MarkdownEditorWidget


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    date_hierarchy = "publication_date"
    list_display = ("id", "title", "type", "publication_date", "is_ready")
    list_filter = ("type", "publication_date")
    search_fields = ("title",)
    # form
    radio_fields = {"type": admin.VERTICAL}
    raw_id_fields = ("event",)
    readonly_fields = ("created_by",)
    inlines = (InstitutionsInline, ProjectsInline, ImagesInline, FilesInline)
    formfield_overrides = {
        models.TextField: {"widget": MarkdownEditorWidget},
    }


@admin.register(Clipping)
class ClippingAdmin(admin.ModelAdmin):
    date_hierarchy = "publication_date"
    list_display = ("id", "title", "publication_date", "external_link")
    list_filter = ("publication_date",)
    search_fields = ("title", "media")

    def external_link(self, obj):
        return format_html(f'<a target="_blank" href="{obj.url}">{obj.media}</a>')


@admin.register(Dissemination)
class DisseminationAdmin(admin.ModelAdmin):
    date_hierarchy = "date"
    list_display = ("id", "event", "type", "date")
    list_filter = ("type", "date")
    # form
    inlines = (FilesInline,)


@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    date_hierarchy = "publication_date"
    list_display = ("id", "title", "event", "publication_date", "downloads")
    list_filter = ("publication_date", ("event", admin.RelatedOnlyFieldListFilter))
    search_fields = ("title",)
    # form
    raw_id_fields = ("event",)
    readonly_fields = ("downloads",)
    inlines = (ApplicationAreasInline, TopicsInline, InstitutionsInline, ProjectsInline, UsersInline, ImagesInline)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("event")


@admin.register(MagazineRecipient)
class MagazineRecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address_line1", "country", "user", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    # form
    raw_id_fields = ("user",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "author", "type", "is_featured")
    list_filter = ("type", "is_featured")
    # form
    inlines = (InstitutionsInline, ProjectsInline, UsersInline)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id", "youtube", "title", "is_expert", "shows_on_homepage")
    list_filter = ("is_expert", "shows_on_homepage")
    search_fields = ("youtube_id", "title")
    # form
    inlines = (InstitutionsInline, ProjectsInline, UsersInline)

    def youtube(self, obj):
        return format_html(f'<a href="https://youtu.be/{obj.youtube_id}" target="_blank">{obj.youtube_id}</a>')

    youtube.short_description = "YouTube ID"


class VideosInline(GenericTabularInline):
    model = RelatedVideo
    classes = ("collapse",)
    extra = 0
    verbose_name = "video"
    # form
    raw_id_fields = ("video",)


class RecordingsInline(VideosInline):
    verbose_name = "recording"
