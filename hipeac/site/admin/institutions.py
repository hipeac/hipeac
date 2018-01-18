from django.contrib import admin

from hipeac.models import Institution
from .generic import HideDeleteActionMixin, LinksInline, PermissionsInline


class InstitutionAdmin(HideDeleteActionMixin, admin.ModelAdmin):
    exclude = ['application_areas', 'topics', 'updated_at']
    inlines = [LinksInline, PermissionsInline]
    raw_id_fields = ['parent']
    search_fields = ['name', 'local_name', 'colloquial_name']

    list_display = ('id', 'name', 'type', 'country')
    list_filter = ('type',)
    fieldsets = (
        (None, {
            'fields': ('type', 'name', 'local_name', 'colloquial_name'),
        }),
        ('INFO', {
            'fields': (('country', 'location'), 'description', 'image'),
        }),
        ('RECRUITMENT', {
            'fields': ('recruitment_contact', 'recruitment_email'),
        }),
    )


admin.site.register(Institution, InstitutionAdmin)
