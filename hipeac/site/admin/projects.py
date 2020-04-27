from django.contrib import admin
from django.forms import ModelForm

from hipeac.forms import ApplicationAreasChoiceField, TopicsChoiceField
from hipeac.models import Project
from .generic import HideDeleteActionMixin, LinksInline, PermissionsInline


class ProjectAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField(required=False)
    topics = TopicsChoiceField(required=False)


@admin.register(Project)
class ProjectAdmin(HideDeleteActionMixin, admin.ModelAdmin):
    form = ProjectAdminForm
    exclude = ("updated_at",)

    list_display = ("id", "ec_project_id", "acronym", "coordinator", "programme", "is_active")
    list_filter = ("programme",)
    search_fields = ("acronym", "name")

    filter_horizontal = ["partners"]
    raw_id_fields = ("coordinating_institution", "coordinator", "communication_officer", "project_officer")
    inlines = (LinksInline, PermissionsInline)
    fieldsets = (
        (None, {"fields": ("acronym", "name")}),
        ("INFO", {"fields": (("start_date", "end_date"), "description", "image")}),
        ("TEAM", {"fields": ("coordinating_institution", "partners", "coordinator", "communication_officer")}),
        ("EC", {"fields": ("programme", "ec_project_id", "project_officer")}),
        ("METADATA", {"classes": ("collapse",), "fields": ("application_areas", "topics")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("coordinator", "programme")
