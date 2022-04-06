from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from hipeac.functions import send_task
from hipeac.models.events.acaces import (
    Acaces,
    AcacesBus,
    AcacesCourse,
    AcacesCourseSession,
    AcacesHotel,
    AcacesPoster,
    AcacesRegistration,
)
from hipeac.models.metadata import Metadata
from hipeac.site.emails.events.acaces import AcacesAdmittedEmail, AcacesPosterAbstractsReminderEmail
from .events import EventAdmin
from .registrations import RegistrationAdmin
from ..communication import RecordingsInline
from ..files import FilesInline
from ..links import LinksInline
from ..metadata import ApplicationAreasInline, TopicsInline
from ..users import TeachersInline
from ..widgets import MarkdownEditorWidget


class AcacesBusesInline(admin.TabularInline):
    model = AcacesBus
    classes = ("collapse",)
    extra = 0
    verbose_name = "bus"
    verbose_name_plural = "buses"


class AcacesCourseSessionsInline(admin.StackedInline):
    model = AcacesCourseSession
    classes = ("collapse",)
    extra = 0
    verbose_name = "session"
    # form
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("start_at", "end_at"),
                    "zoom_webinar_id",
                    "zoom_attendee_report",
                )
            },
        ),
    )


class AcacesHotelsInline(admin.TabularInline):
    model = AcacesHotel
    classes = ("collapse",)
    extra = 0
    verbose_name = "hotel"


class AcacesPosterInline(admin.StackedInline):
    model = AcacesPoster
    classes = ("collapse",)
    extra = 0
    verbose_name = "poster"


@admin.register(Acaces)
class AcacesAdmin(EventAdmin):
    list_display = EventAdmin.list_display + ("courses_link",)
    # form
    fieldsets = EventAdmin.fieldsets + (
        (
            "Fees",
            {"classes": ("collapse",), "fields": ("fee", "shared_room_discount", "grant_request_deadline")},
        ),
    )
    inlines = EventAdmin.inlines + [AcacesHotelsInline, AcacesBusesInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(models.Count("courses", distinct=True))

    def courses_link(self, obj):
        if obj.courses__count == 0:
            return "-"
        url = reverse("admin:hipeac_acacescourse_changelist")
        return format_html(f'<a href="{url}?event__event_ptr__exact={obj.id}">{obj.courses__count}</a>')

    courses_link.short_description = "Courses"


@admin.register(AcacesCourse)
class AcacesCourseAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "slot", "title")
    list_filter = ("slot", "event")
    search_fields = ("title",)
    # form
    inlines = (
        TeachersInline,
        AcacesCourseSessionsInline,
        ApplicationAreasInline,
        TopicsInline,
        LinksInline,
        FilesInline,
        RecordingsInline,
    )
    formfield_overrides = {
        models.TextField: {"widget": MarkdownEditorWidget},
    }


# @admin.register(AcacesGrant)
class AcacesGrantAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "country", "available_grants")
    list_filter = ("event",)
    search_fields = ("country",)


@admin.register(AcacesRegistration)
class AcacesRegistrationAdmin(RegistrationAdmin):
    actions = (
        ("admit_and_send_email",)
        + RegistrationAdmin.actions
        + (
            "send_payment_reminder",
            "send_acaces_poster_abstract_reminder",
            "update_user_profile",
        )
    )
    list_display = RegistrationAdmin.list_display + ("grant", "status", "accepted")
    list_filter = ("status", "accepted", "grant_requested", "grant_assigned") + RegistrationAdmin.list_filter
    # form
    filter_horizontal = RegistrationAdmin.filter_horizontal + ("courses",)
    raw_id_fields = RegistrationAdmin.raw_id_fields + ("roommate",)
    readonly_fields = RegistrationAdmin.readonly_fields + ("accepted", "grant_requested")
    fieldsets = RegistrationAdmin.fieldsets + (
        ("Application", {"fields": ("status", "accepted", "grant_requested", "grant_assigned")}),
        ("Hotel", {"fields": ("assigned_hotel", "roommate_requested", "roommate_notes", "roommate")}),
        (
            "Course selection and Motivation",
            {"classes": ("collapse",), "fields": ("motivation", "courses", "sessions", "custom_data")},
        ),
        (
            "Travel information",
            {
                "classes": ("collapse",),
                "fields": ("arrival_flight", "arrival_bus", "departure_bus", "departure_flight", "phone_number"),
            },
        ),
    )
    inlines = RegistrationAdmin.inlines + (AcacesPosterInline,)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            readonly_fields = super().get_readonly_fields(request, obj)
        else:
            readonly_fields = super().get_readonly_fields(request, obj) + ("custom_data",)

        if not self.instance:
            return readonly_fields + ("assigned_hotel", "arrival_bus", "courses", "departure_bus", "roommate")
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not self.instance:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == "assigned_hotel":
            kwargs["queryset"] = AcacesHotel.objects.filter(event_id=self.instance.event_id)
        if db_field.name == "arrival_bus":
            kwargs["queryset"] = AcacesBus.objects.filter(
                event_id=self.instance.event_id, destination=AcacesBus.DESTINATION_SCHOOL
            )
        if db_field.name == "departure_bus":
            kwargs["queryset"] = AcacesBus.objects.filter(
                event_id=self.instance.event_id, destination=AcacesBus.DESTINATION_HOME
            )
        if db_field.name == "roommate":
            kwargs["queryset"] = AcacesRegistration.objects.filter(event_id=self.instance.event_id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "courses" and self.instance:
            kwargs["queryset"] = AcacesCourse.objects.filter(event_id=self.instance.event_id)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # custom actions

    def admit_and_send_email(self, request, queryset):
        """This is not very efficient but we need it to make sure fees are recalculated."""
        for instance in queryset:
            instance.status = AcacesRegistration.STATUS_ADMITTED
            instance.save()
            email = AcacesAdmittedEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Accepted. Emails are being sent.")

    def send_acaces_poster_abstract_reminder(self, request, queryset):
        for instance in queryset:
            email = AcacesPosterAbstractsReminderEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    def update_user_profile(self, request, queryset):
        for instance in queryset:
            profile = instance.user.profile
            save = False
            if not profile.country:
                save = True
                profile.country = instance.custom_data["profile"]["country"]["value"]
            if not profile.gender:
                save = True
                profile.gender = Metadata.objects.get(
                    type=Metadata.GENDER,
                    value={"female": "Female", "male": "Male", "non_binary": "Non-binary"}[
                        instance.custom_data["profile"]["gender"]
                    ],
                )
            if save:
                profile.save()
        admin.ModelAdmin.message_user(self, request, "User profiles updated.")

    admit_and_send_email.short_description = "✅ Admit and send email"
    send_acaces_poster_abstract_reminder.short_description = "➡️ Send poster reminder to users"
    update_user_profile.short_description = "🔄 Update user profile"

    # custom fields

    def grant(self, obj):
        requested = "yes" if obj.grant_requested else "no"
        assigned = {
            True: "yes",
            False: "no",
            None: "unknown",
        }[obj.grant_assigned]
        return format_html(
            '<span class="text-nowrap">'
            f'<img src="/static/admin/img/icon-{requested}.svg" title="Grant requested: {requested}">'
            " / "
            f'<img src="/static/admin/img/icon-{assigned}.svg" title="Grant assigned: {assigned}">'
            "</span>"
        )
