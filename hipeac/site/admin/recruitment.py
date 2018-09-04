from django.contrib import admin

from hipeac.models import Job
from .generic import HideDeleteActionMixin, LinksInline, PermissionsInline


@admin.register(Job)
class JobAdmin(HideDeleteActionMixin, admin.ModelAdmin):
    date_hierarchy = 'created_at'
    exclude = ['application_areas', 'topics', 'updated_at']
    inlines = [LinksInline, PermissionsInline]
    list_display = ('id', 'title', 'institution', 'deadline', 'created_at')
    radio_fields = {'employment_type': admin.VERTICAL}
    raw_id_fields = ['institution', 'project']

    fieldsets = (
        (None, {
            'fields': ('title', 'institution', 'project'),
        }),
        ('INFO', {
            'fields': (('country', 'location'), 'description', 'positions', 'deadline'),
        }),
        ('CONTACT', {
            'fields': ('email',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('institution')
