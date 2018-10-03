from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.models import Image, Link, Permission


class HideDeleteActionMixin:
    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.is_superuser and 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class ImagesInline(GenericTabularInline):
    model = Image
    classes = ('collapse',)
    extra = 0


class LinksInline(GenericTabularInline):
    model = Link
    classes = ('collapse',)
    extra = 0


class PermissionsInline(GenericTabularInline):
    model = Permission
    classes = ('collapse',)
    extra = 0
    raw_id_fields = ('user',)
