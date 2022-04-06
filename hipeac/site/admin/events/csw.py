from django.contrib import admin

from hipeac.functions import send_task
from hipeac.models.events.csw import Csw, CswRegistration
from hipeac.site.emails.events.events import NoShowsEmail
from .events import EventAdmin
from .registrations import RegistrationAdmin
from ..generic import clean_tuple


@admin.register(Csw)
class CswAdmin(EventAdmin):
    pass


@admin.register(CswRegistration)
class CswRegistrationAdmin(RegistrationAdmin):
    actions = RegistrationAdmin.actions + ("send_no_show_reminder",)
    list_display = clean_tuple(RegistrationAdmin.list_display, ["invoice"])
    list_filter = clean_tuple(RegistrationAdmin.list_filter, ["invoice_requested", "invoice_sent"])
    # form
    fieldsets = RegistrationAdmin.fieldsets + (("Sessions", {"classes": ("collapse",), "fields": ("sessions",)}),)

    # custom actions

    def send_no_show_reminder(self, request, queryset):
        for instance in queryset:
            email = NoShowsEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    send_no_show_reminder.short_description = "➡️ Send no-shows reminder to users"
