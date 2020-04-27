from django.contrib import admin

from hipeac.models import Vision
from .generic import ImagesInline, LinksInline, PublicFilesInline


@admin.register(Vision)
class VisionAdmin(admin.ModelAdmin):
    date_hierarchy = "publication_date"
    list_display = ("id", "title", "publication_date", "downloads")

    inlines = (LinksInline, ImagesInline, PublicFilesInline)
    readonly_fields = ("downloads",)
