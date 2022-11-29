from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.models.permissions import Permission


class PermissionsInline(GenericTabularInline):
    model = Permission
    classes = ("collapse",)
    extra = 0
    verbose_name = "manager"
    # form
    raw_id_fields = ("user",)
