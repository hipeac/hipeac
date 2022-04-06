from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.models import Image


class ImagesInline(GenericTabularInline):
    model = Image
    classes = ("collapse",)
    extra = 0
