from django.contrib import admin

from hipeac.models.events import Room, Venue
from ..links import LinksInline


class RoomsInline(admin.TabularInline):
    model = Room
    classes = ("collapse",)
    extra = 0
    verbose_name = "room"


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "max_capacity", "venue")
    search_fields = ("name", "venue__name", "venue__city")
    # form
    raw_id_fields = ("venue",)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("venue")

    def has_module_permission(self, request):
        return False


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "country")
    search_fields = ("name", "city")
    # form
    inlines = [RoomsInline, LinksInline]

    def has_module_permission(self, request):
        return request.user.is_superuser
