from django.contrib import admin

from hipeac.models import Webinar


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    exclude = ("updated_at",)

    autocomplete_fields = ("event", "projects", "main_speaker", "speakers")
