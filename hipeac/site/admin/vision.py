from django.contrib import admin

from hipeac.models import Vision
from .generic import ImagesInline, LinksInline, PublicFilesInline


@admin.register(Vision)
class VisionAdmin(admin.ModelAdmin):
    inlines = (LinksInline, ImagesInline, PublicFilesInline)
    readonly_fields = ('downloads',)
