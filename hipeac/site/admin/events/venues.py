from django.contrib import admin

from hipeac.models.events import Room, Venue
from ..links import LinksInline


class RoomsInline(admin.TabularInline):
    model = Room
    classes = ("collapse",)
    extra = 0
    verbose_name = "room"


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "country")
    search_fields = ("name", "city")
    # form
    inlines = [RoomsInline, LinksInline]

    def has_module_permission(self, request):
        return request.user.is_superuser
