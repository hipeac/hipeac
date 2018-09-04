from django.contrib import admin

from hipeac.models import Project
from .generic import HideDeleteActionMixin, LinksInline, PermissionsInline


@admin.register(Project)
class ProjectAdmin(HideDeleteActionMixin, admin.ModelAdmin):
    exclude = ['application_areas', 'topics', 'updated_at']
    filter_horizontal = ['partners']
    inlines = [LinksInline, PermissionsInline]
    list_display = ('id', 'ec_project_id', 'acronym', 'coordinator', 'programme', 'is_active')
    list_filter = ('programme',)
    raw_id_fields = ['coordinating_institution', 'coordinator', 'communication_officer', 'project_officer']
    search_fields = ['acronym', 'name']

    fieldsets = (
        (None, {
            'fields': ('acronym', 'name'),
        }),
        ('INFO', {
            'fields': (('start_date', 'end_date'), 'description', 'image'),
        }),
        ('TEAM', {
            'fields': ('coordinating_institution', 'partners', 'coordinator', 'communication_officer'),
        }),
        ('EC', {
            'fields': ('programme', 'ec_project_id', 'project_officer'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('coordinator')
