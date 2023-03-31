from django.contrib import admin, messages

from hipeac.models import Email, EmailRecipient
from hipeac.services.mailer import TemplateEmail


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    actions = ("send_custom_email",)
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

    @admin.action(description="✉️ Send to custom list")
    def send_custom_email(self, request, queryset):
        if queryset.count() > 1 or not queryset.first().code.startswith("custom"):
            messages.warning(request, "Please select only one email of type `custom`.")
            return

        email = queryset.first()

        for recipient in EmailRecipient.objects.filter(code=email.code):
            TemplateEmail(email.code, to=[recipient.email], instance=recipient).send()

        messages.info(request, "Messages are being sent.")
