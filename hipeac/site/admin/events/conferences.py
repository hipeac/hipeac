from django.contrib import admin

from hipeac.models.events.conferences import Conference, ConferenceRegistration, ConferenceSponsor
from .events import EventAdmin
from .registrations import RegistrationAdmin


class ConferenceSponsorsInline(admin.TabularInline):
    model = ConferenceSponsor
    classes = ("collapse",)
    extra = 0
    verbose_name = "sponsor"
    # form
    raw_id_fields = ("institution", "project")


@admin.register(Conference)
class ConferenceAdmin(EventAdmin):
    fieldsets = EventAdmin.fieldsets + (
        (
            "Fees",
            {
                "classes": ("collapse",),
                "fields": (("fee", "student_fee"), ("early_fee", "early_student_fee"), "booth_fee"),
            },
        ),
    )
    inlines = EventAdmin.inlines + [ConferenceSponsorsInline]


@admin.register(ConferenceRegistration)
class ConferenceRegistrationAdmin(RegistrationAdmin):
    actions = RegistrationAdmin.actions + ("send_payment_reminder",)
    fieldsets = RegistrationAdmin.fieldsets + (("Sessions", {"classes": ("collapse",), "fields": ("sessions",)}),)
