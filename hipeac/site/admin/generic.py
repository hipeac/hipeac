from django.contrib.admin import FieldListFilter
from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.models import Image, Link, Permission, PrivateFile, PublicFile


def custom_titled_filter(title):
    # https://stackoverflow.com/questions/17392087/how-to-modify-django-admin-filters-title

    class Wrapper(FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class HideDeleteActionMixin:
    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.is_superuser and "delete_selected" in actions:
            del actions["delete_selected"]
        return actions


class ImagesInline(GenericTabularInline):
    model = Image
    classes = ("collapse",)
    extra = 0


class LinksInline(GenericTabularInline):
    model = Link
    classes = ("collapse",)
    extra = 0


class PermissionsInline(GenericTabularInline):
    model = Permission
    classes = ("collapse",)
    extra = 0
    autocomplete_fields = ("user",)


class PrivateFilesInline(GenericTabularInline):
    model = PrivateFile
    classes = ("collapse",)
    extra = 0


class PublicFilesInline(GenericTabularInline):
    model = PublicFile
    classes = ("collapse",)
    extra = 0
