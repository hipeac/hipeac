from django.contrib import admin

from hipeac.models import Vision
from .generic import ImagesInline


@admin.register(Vision)
class VisionAdmin(admin.ModelAdmin):
    inlines = (ImagesInline,)
