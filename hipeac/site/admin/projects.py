from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.models.projects import Project, RelatedProject
from .institutions import PartnersInline
from .links import LinksInline
from .metadata import ApplicationAreasInline, TopicsInline
from .permissions import PermissionsInline


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ("id", "is_visible", "acronym", "name")
    list_filter = ("is_visible", "created_at")
    search_fields = ("acronym", "name")
    # form
    raw_id_fields = ("coordinator", "coordinating_institution", "communication_officer")
    readonly_fields = ("created_by",)
    inlines = (PartnersInline, ApplicationAreasInline, TopicsInline, LinksInline, PermissionsInline)


class ProjectsInline(GenericTabularInline):
    model = RelatedProject
    classes = ("collapse",)
    extra = 0
    verbose_name = "project"
    # form
    raw_id_fields = ("project",)
