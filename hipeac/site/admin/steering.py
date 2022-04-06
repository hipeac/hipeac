from django.contrib import admin
from django.db import models

from hipeac.models.steering import ActionPoint, Meeting
from .files import FilesInline
from .users import OwnersInline
from .widgets import MarkdownEditorWidget


@admin.register(ActionPoint)
class ActionPointdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ("id", "title", "status")
    list_filter = ("status",)
    search_fields = ("id", "title")
    # form
    inlines = (OwnersInline, FilesInline)


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    date_hierarchy = "start_at"
    list_display = ("id", "start_at", "location")
    # form
    inlines = (FilesInline,)
    formfield_overrides = {
        models.TextField: {"widget": MarkdownEditorWidget},
    }
