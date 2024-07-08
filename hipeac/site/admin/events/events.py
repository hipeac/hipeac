from django.contrib import admin, messages
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from hipeac.models.events import AcacesRegistration, Break, Committee, Event
from hipeac.site.pdfs.redux.events.badges import BadgesPdfMaker
from hipeac.site.sheets.events.registrations import RegistrationsSheet

from ..communication import VideosInline
from ..links import LinksInline
from ..users import MembersInline
from ..widgets import MarkdownEditorWidget


class BreaksInline(admin.TabularInline):
    model = Break
    classes = ("collapse",)
    extra = 0
    verbose_name = "break"


@admin.register(Committee)
class CommitteesInline(admin.ModelAdmin):
    list_display = ("id", "name", "event")
    list_filter = (("event", admin.RelatedOnlyFieldListFilter),)
    # form
    inlines = (MembersInline,)

    def has_module_permission(self, request):
        return request.user.is_superuser


class EventAdmin(admin.ModelAdmin):
    actions = ("excel_overview", "pdf_badges")
    list_display = (
        "id",
        "name",
        "city",
        "start_date",
        "end_date",
        "is_virtual",
        "is_active",
        "is_open",
        "registrations_link",
        "sessions_link",
    )
    search_fields = ("city", "country", "start_date__year")
    # form
    raw_id_fields = ("coordinating_institution", "venue")
    fieldsets = (
        (
            None,
            {"fields": ("is_virtual", "hashtag")},
        ),
        (
            "Dates",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "registration_start_date",
                    ("registration_early_deadline", "registration_deadline"),
                ),
            },
        ),
        (
            "General information",
            {
                "classes": ("collapse",),
                "fields": (
                    "coordinating_institution",
                    "city",
                    "country",
                    "presentation",
                    "logistics",
                    "venue",
                    "image",
                ),
            },
        ),
        (
            "Payment bridge",
            {
                "classes": ("collapse",),
                "fields": ("wbs_element", "ingenico_salt", "payments_activation", "allows_invoices"),
            },
        ),
    )
    formfield_overrides = {
        models.TextField: {"widget": MarkdownEditorWidget},
    }

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(models.Count("registrations", distinct=True))
            .annotate(models.Count("sessions", distinct=True))
        )

    def get_inlines(self, request, obj=None):
        return super().get_inlines(request, obj) + (BreaksInline, LinksInline, VideosInline)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ("registrations_count",)
        return ("registrations_count", "wbs_element", "ingenico_salt")

    # custom actions

    @admin.action(description="🔡 Attendees overview")
    def excel_overview(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "Please select only one event.")
            return

        event = queryset.first()
        return RegistrationsSheet(
            filename=f"{event.year}-{event.slug}-overview.xlsx", queryset=event.registrations
        ).response

    @admin.action(description="ℹ️ Download badges")
    def pdf_badges(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "Please select only one event.")
            return

        event = queryset.first()
        registrations = event.registrations

        if event.type == Event.ACACES:
            registrations = AcacesRegistration.objects.filter(
                event=event, status=AcacesRegistration.STATUS_ADMITTED, accepted=True
            )

        return BadgesPdfMaker(registrations=registrations, filename=f"{event.year}-{event.slug}-badges.pdf").response

    # custom fields

    def is_active(self, obj) -> bool:
        return obj.is_active()

    def is_open(self, obj) -> bool:
        return obj.is_open_for_registration()

    def registrations_link(self, obj):
        if obj.registrations__count == 0:
            return "-"

        try:
            url_prefix = {
                Event.ACACES: "hipeac_acacesregistration",
                Event.CONFERENCE: "hipeac_conferenceregistration",
                Event.CSW: "hipeac_cswregistration",
            }[obj.type]
        except KeyError:
            url_prefix = "hipeac_registration"

        url = reverse(f"admin:{url_prefix}_changelist")
        return format_html(f'<a href="{url}?event__id__exact={obj.id}">{obj.registrations__count}</a>')

    def sessions_link(self, obj):
        if obj.sessions__count == 0:
            return "-"
        url = reverse("admin:hipeac_session_changelist")
        return format_html(f'<a href="{url}?event__id__exact={obj.id}">{obj.sessions__count}</a>')

    is_active.boolean = True
    is_active.short_description = "Active"
    is_open.boolean = True
    is_open.short_description = "Open"
    registrations_link.short_description = "Registrations"
    sessions_link.short_description = "Sessions"


@admin.register(Event)
class EventHiddenAdmin(EventAdmin):
    def has_module_permission(self, request):
        return False
