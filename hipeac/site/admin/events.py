from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe

from hipeac.models import Event, Registration, Roadshow, Session
from .generic import ImagesInline, LinksInline


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_date'
    inlines = (LinksInline,)
    list_display = ('id', 'start_date', 'end_date', 'name', 'type', 'sessions_link', 'registrations_link',
                    'is_active', 'is_open')
    list_filter = ('type',)
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(Count('sessions', distinct=True)) \
                                            .annotate(Count('registrations', distinct=True))

    def is_active(self, obj) -> bool:
        return obj.is_active()
    is_active.boolean = True
    is_active.short_description = 'Active'

    def is_open(self, obj) -> bool:
        return obj.is_open_for_registration()
    is_open.boolean = True
    is_open.short_description = 'Open'

    def registrations_link(self, obj):
        if obj.registrations__count == 0:
            return '-'
        url = reverse('admin:hipeac_registration_changelist')
        return mark_safe(f'<a href="{url}?event__id__exact={obj.id}">{obj.registrations__count}</a>')
    registrations_link.short_description = 'Registrations'

    def sessions_link(self, obj):
        if obj.sessions__count == 0:
            return '-'
        url = reverse('admin:hipeac_session_changelist')
        return mark_safe(f'<a href="{url}?event__id__exact={obj.id}">{obj.sessions__count}</a>')
    sessions_link.short_description = 'Sessions'


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_filter = ('event',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('user', 'event')


@admin.register(Roadshow)
class RoadshowAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_date'
    inlines = (ImagesInline, LinksInline)
    list_display = ('id', 'name', 'country', 'start_date', 'end_date')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_filter = ('event',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('event')
