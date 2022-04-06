from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.models import File


class FilesInline(GenericTabularInline):
    model = File
    classes = ("collapse",)
    extra = 0
