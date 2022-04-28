from django.contrib import admin

from hipeac.models.events.csw import Csw, CswRegistration
from .events import EventAdmin
from .registrations import RegistrationAdmin
from ..generic import clean_tuple


@admin.register(Csw)
class CswAdmin(EventAdmin):
    pass


@admin.register(CswRegistration)
class CswRegistrationAdmin(RegistrationAdmin):
    email_actions = RegistrationAdmin.email_actions + ["events.csw.registration."]
    list_display = clean_tuple(RegistrationAdmin.list_display, ["invoice"])
    list_filter = clean_tuple(RegistrationAdmin.list_filter, ["invoice_requested", "invoice_sent"])
    # form
    fieldsets = RegistrationAdmin.fieldsets + (("Sessions", {"classes": ("collapse",), "fields": ("sessions",)}),)
