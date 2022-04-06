from django.contrib import admin

from hipeac.models.vision import Vision, VisionArticle
from .communication import VideosInline
from .files import FilesInline
from .images import ImagesInline
from .links import LinksInline


class VisionArticleInline(admin.TabularInline):
    model = VisionArticle
    classes = ("collapse",)
    extra = 0
    verbose_name = "article"


@admin.register(Vision)
class VisionAdmin(admin.ModelAdmin):
    date_hierarchy = "publication_date"
    list_display = ("id", "title", "publication_date", "downloads")

    inlines = (VisionArticleInline, LinksInline, ImagesInline, FilesInline, VideosInline)
    readonly_fields = ("downloads",)
