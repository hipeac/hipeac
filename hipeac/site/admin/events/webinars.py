from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from hipeac.models.events.webinars import Webinar, WebinarRegistration, WebinarProposal
from ..communication import RecordingsInline
from ..files import FilesInline
from ..institutions import InstitutionsInline
from ..metadata import ApplicationAreasInline, TopicsInline
from ..projects import ProjectsInline
from ..users import SpeakersInline


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    date_hierarchy = "start_at"
    list_display = ("id", "zoom_id", "title", "start_at", "is_open", "registrations_link")
    search_fields = ("title", "zoom_webinar_id")
    # form
    raw_id_fields = ("main_speaker",)
    readonly_fields = ("keywords",)
    fieldsets = (
        (None, {"fields": ("start_at", "end_at")}),
        ("Zoom", {"fields": ("zoom_webinar_id", "zoom_attendee_report")}),
        ("General information", {"fields": ("type", "title", "summary", "program", "organizers", "keywords")}),
    )
    inlines = [
        ApplicationAreasInline,
        TopicsInline,
        ProjectsInline,
        InstitutionsInline,
        SpeakersInline,
        RecordingsInline,
        FilesInline,
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(Count("registrations", distinct=True))

    def is_open(self, obj) -> bool:
        return obj.is_open_for_registration()

    def registrations_link(self, obj):
        if obj.registrations__count == 0:
            return "-"
        url = reverse("admin:hipeac_webinarregistration_changelist")
        return format_html(f'<a href="{url}?webinar__id__exact={obj.id}">{obj.registrations__count}</a>')

    def zoom_id(self, obj):
        return format_html(obj.zoom_webinar_id.replace(" ", "&nbsp;")) if obj.zoom_webinar_id else "-"

    is_open.boolean = True
    is_open.short_description = "Open"
    registrations_link.short_description = "Registrations"


@admin.register(WebinarRegistration)
class WebinarRegistrationAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ("id", "created_at", "user")
    # form
    raw_id_fields = ("user", "webinar")
    readonly_fields = ("created_at", "updated_at", "zoom_access_link")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user__profile__institution")

    def has_module_permission(self, request):
        return request.user.is_superuser

    def name(self, obj):
        institution = obj.user.profile.institution.short_name if obj.user.profile.institution else "-"
        url = reverse("admin:auth_user_changelist")
        return format_html(
            f'<a href="{url}{obj.user_id}/" target="admin_user">{obj.user.profile.name}</a>, {institution}'
        )


@admin.register(WebinarProposal)
class WebinarProposalAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user")

    def user(self, obj):
        return f"{obj.first_name} {obj.last_name} <{obj.email}>"
