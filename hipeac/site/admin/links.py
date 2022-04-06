from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.models import Link


class LinksInline(GenericTabularInline):
    model = Link
    classes = ("collapse",)
    extra = 0
