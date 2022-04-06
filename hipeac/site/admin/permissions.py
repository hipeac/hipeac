from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.models.permissions import Permission


class PermissionsInline(GenericTabularInline):
    model = Permission
    classes = ("collapse",)
    extra = 0
    # form
    raw_id_fields = ("user",)
