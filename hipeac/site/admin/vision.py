from django.contrib import admin

from hipeac.models import Vision, VisionArticle
from .generic import ImagesInline, LinksInline, PublicFilesInline


class VisionArticleInline(admin.TabularInline):
    model = VisionArticle
    classes = ("collapse",)
    extra = 0


@admin.register(Vision)
class VisionAdmin(admin.ModelAdmin):
    date_hierarchy = "publication_date"
    list_display = ("id", "title", "publication_date", "downloads")

    inlines = (LinksInline, ImagesInline, PublicFilesInline, VisionArticleInline)
    readonly_fields = ("downloads",)
