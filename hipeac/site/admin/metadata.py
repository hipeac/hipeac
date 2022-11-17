from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.models.metadata import Metadata, ApplicationArea, Topic


@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "value", "position", "keywords")
    list_filter = ("type",)
    search_fields = ("value", "keywords")
    # form
    fieldsets = ((None, {"fields": ("type", "value", "position", "keywords")}),)


class ApplicationAreasInline(GenericTabularInline):
    model = ApplicationArea
    classes = ("collapse",)
    extra = 0
    # form
    autocomplete_fields = ("application_area",)


class TopicsInline(GenericTabularInline):
    model = Topic
    classes = ("collapse",)
    extra = 0
    # form
    autocomplete_fields = ("topic",)
