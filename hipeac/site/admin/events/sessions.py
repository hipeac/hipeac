from django.contrib import admin, messages
from django.db.models import Count

from hipeac.models.events import Session
from hipeac.site.sheets.events.registrations import RegistrationsSheet
from ..communication import VideosInline
from ..generic import include_email_actions
from ..files import FilesInline
from ..institutions import InstitutionsInline
from ..links import LinksInline
from ..metadata import ApplicationAreasInline, TopicsInline
from ..permissions import PermissionsInline
from ..projects import ProjectsInline
from ..users import SpeakersInline


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    email_actions = ["events.session.organizers."]
    actions = ("excel_overview", "send_reminder", "send_speakers_reminder", "send_proceedings_reminder")
    date_hierarchy = "start_at"
    list_display = ("id", "title", "start_at", "end_at", "type", "registrations_count")
    list_filter = ("type", ("event", admin.RelatedOnlyFieldListFilter))
    search_fields = ("title",)
    # form
    radio_fields = {"type": admin.VERTICAL}
    raw_id_fields = ("event", "main_speaker", "room")
    fieldsets = (
        (None, {"fields": ("event", ("start_at", "end_at"), "type", "is_private")}),
        ("General information", {"fields": ("title", "main_speaker", "summary", "program", "organizers")}),
        ("Room and extra fees", {"fields": ("room", "max_attendees", "extra_attendees_fee")}),
        ("Zoom", {"fields": ("zoom_webinar_id", "zoom_attendee_report")}),
    )
    inlines = (
        ApplicationAreasInline,
        TopicsInline,
        ProjectsInline,
        InstitutionsInline,
        SpeakersInline,
        LinksInline,
        FilesInline,
        VideosInline,
        PermissionsInline,
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("event", "type")
            .annotate(Count("registrations", distinct=True))
        )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if self.email_actions:
            for prefix in self.email_actions:
                actions = include_email_actions(actions, prefix)
        return actions

    # custom actions

    @admin.action(description="🔡 Attendees overview")
    def excel_overview(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "Please select only one session.")
            return

        return RegistrationsSheet(
            filename=f"{queryset.first().id}-session-overview.xlsx", queryset=queryset.first().registrations
        ).response

    # custom fields

    def registrations_count(self, obj):
        return obj.registrations__count if obj.registrations__count > 0 else "-"

    registrations_count.short_description = "Registrations"
