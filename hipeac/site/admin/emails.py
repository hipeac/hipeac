from django.contrib import admin

from hipeac.models import Email


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "subject", "from_email")
    search_fields = ("code", "subject")
    # form
    fieldsets = (
        (None, {"fields": ("code", "action_name", "position")}),
        (
            "Email",
            {
                "fields": (
                    ("from_email", "reply_to_email"),
                    "cc_emails",
                    "subject",
                    "template",
                ),
            },
        ),
    )
