from django.contrib import admin, messages
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

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
from hipeac.site.pdfs.redux.events.acaces import merge_abstract_pdfs
from .events import EventAdmin
from .registrations import RegistrationAdmin
from ..communication import RecordingsInline
from ..files import FilesInline
from ..links import LinksInline
from ..metadata import ApplicationAreasInline, TopicsInline
from ..users import TeachersInline
from ..widgets import MarkdownEditorWidget


def create_hotel_action(hotel: AcacesHotel) -> callable:
    def assign_hotel(modeladmin, request, queryset):
        for instance in queryset:
            instance.assigned_hotel = hotel
            instance.save()
        messages.info(request, "Hotel has been assigned.")

    assign_hotel.short_description = f'🏨 Assign hotel "{hotel.code}": {hotel.name}'
    assign_hotel.__name__ = f"acaces_hotel.{hotel.id}".replace(".", "_")

    return assign_hotel


def include_hotel_actions(actions: dict, event) -> dict:
    for hotel in event.hotels.order_by("name"):
        action = create_hotel_action(hotel)
        actions[action.__name__] = (action, action.__name__, action.short_description)

    return actions


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
    actions = EventAdmin.actions + ("download_abstracts",)
    list_display = EventAdmin.list_display + ("courses_link",)
    # form
    fieldsets = EventAdmin.fieldsets + (
        (
            "Fees",
            {"classes": ("collapse",), "fields": ("fee", "shared_room_discount", "grant_request_deadline")},
        ),
    )
    inlines = EventAdmin.inlines + (AcacesHotelsInline, AcacesBusesInline)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(models.Count("courses", distinct=True))

    # custom actions

    @admin.action(description="🔽 Download book of abstracts")
    def download_abstracts(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "Please select only one event.")
            return

        acaces = queryset.first()
        return merge_abstract_pdfs(acaces, filename=f"acaces{acaces.year}-abstracts.pdf", as_attachment=True)

    # custom fields

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
    email_actions = ["events.acaces.registration."] + RegistrationAdmin.email_actions
    list_display = RegistrationAdmin.list_display + ("grant", "status", "accepted", "hotel")
    list_filter = (
        (
            "status",
            "accepted",
            "grant_requested",
            "grant_assigned",
            "roommate_requested",
            "user__profile__meal_preference",
        )
        + RegistrationAdmin.list_filter
        + (("assigned_hotel", admin.RelatedOnlyFieldListFilter),)
    )
    # form
    filter_horizontal = RegistrationAdmin.filter_horizontal + ("courses",)
    raw_id_fields = RegistrationAdmin.raw_id_fields + ("roommate",)
    readonly_fields = RegistrationAdmin.readonly_fields + ("grant_requested",)
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

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("assigned_hotel")

    def get_actions(self, request):
        actions = super().get_actions(request)
        try:
            actions = include_hotel_actions(actions, Acaces.objects.get(id=request.GET["event__id__exact"]))
        except KeyError:
            pass
        return actions

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

    @admin.action(description="🔄 Update user profile")
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

    # custom fields

    def hotel(self, obj):
        return obj.assigned_hotel.code if obj.assigned_hotel else "-"

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
