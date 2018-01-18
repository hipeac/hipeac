from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.models import Link, Permission


class HideDeleteActionMixin:
    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.is_superuser and 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class LinksInline(GenericTabularInline):
    classes = ['collapse']
    extra = 0
    model = Link


class PermissionsInline(GenericTabularInline):
    classes = ['collapse']
    extra = 0
    model = Permission
    raw_id_fields = ['user']
