from django.contrib import admin, messages
from django.db.models import Count

from hipeac.functions import send_task
from hipeac.models.events import Session
from hipeac.site.emails.events.events import (
    SessionProceedingsEmail,
    SessionReminderEmail,
    SessionSpeakersReminderEmail,
)
from hipeac.site.sheets.events.registrations import RegistrationsSheet
from ..communication import VideosInline
from ..files import FilesInline
from ..institutions import InstitutionsInline
from ..links import LinksInline
from ..metadata import ApplicationAreasInline, TopicsInline
from ..permissions import PermissionsInline
from ..projects import ProjectsInline
from ..users import SpeakersInline


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    actions = ("excel_overview", "send_reminder", "send_speakers_reminder", "send_proceedings_reminder")
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

    # custom actions

    @admin.action(description="🔡 Attendees overview")
    def excel_overview(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "Please select only one session.")
            return

        return RegistrationsSheet(
            filename=f"{queryset.first().id}-session-overview.xlsx", queryset=queryset.first().registrations
        ).response

    @admin.action(description="➡️ Ask proceedings to organizers")
    def send_proceedings_reminder(self, request, queryset):
        for instance in queryset:
            if instance.acl.count() == 0:
                continue
            email = SessionProceedingsEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    @admin.action(description="➡️ Send reminder to organizers")
    def send_reminder(self, request, queryset):
        for instance in queryset:
            if instance.acl.count() == 0:
                continue
            email = SessionReminderEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    @admin.action(description="➡️ Send speakers reminder to organizers")
    def send_speakers_reminder(self, request, queryset):
        for instance in queryset:
            if instance.acl.count() == 0:
                continue
            email = SessionSpeakersReminderEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    # custom fields

    def registrations_count(self, obj):
        return obj.registrations__count if obj.registrations__count > 0 else "-"

    registrations_count.short_description = "Registrations"
