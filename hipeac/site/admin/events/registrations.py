from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import path, reverse
from django.utils.html import format_html

from hipeac.functions import send_task
from hipeac.models.events import Coupon, InvitationLetter, Registration, Session
from hipeac.site.emails.events.events import RegistrationReminderEmail
from hipeac.site.pdfs.redux.events.badges import BadgesPdfMaker
from ..users import send_profile_update_reminders


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "value", "event", "notes")
    list_filter = (("event", admin.RelatedOnlyFieldListFilter),)
    search_fields = ("code", "notes")


class InvitationLetterInline(admin.StackedInline):
    model = InvitationLetter
    classes = ("collapse",)
    extra = 0
    verbose_name = "invitation letter"


class RegistrationIsPaidFilter(admin.SimpleListFilter):
    title = "payment status"
    parameter_name = "paid"

    def lookups(self, request, model_admin):
        return (
            ("y", "Paid"),
            ("c", "Paid, using a coupon"),
            ("n", "Not paid, no invoice"),
            ("i", "Not paid, but requested invoice"),
        )

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.filter(saldo__gte=0)
        if self.value() == "c":
            return queryset.filter(saldo__gte=0, coupon__isnull=False)
        if self.value() == "n":
            return queryset.filter(saldo__lt=0, invoice_requested=False)
        if self.value() == "i":
            return queryset.filter(saldo__lt=0, invoice_requested=True)
        return queryset


class RegistrationAdmin(admin.ModelAdmin):
    actions = (
        "pdf_badges",
        "send_reminder",
        "send_profile_update_reminder",
        "send_visa_reminder",
    )
    date_hierarchy = "created_at"
    list_display = (
        "id",
        "created_at",
        "name",
        "fee",
        "is_paid",
        "with_coupon",
        "invoice",
        "visa",
    )
    list_filter = (
        RegistrationIsPaidFilter,
        "invoice_requested",
        "invoice_sent",
        "visa_requested",
        "visa_sent",
        ("event", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("id", "user__email", "user__username", "user__first_name", "user__last_name")
    # form
    filter_horizontal = ("sessions",)
    raw_id_fields = ("event", "user", "coupon")
    readonly_fields = ("created_at", "updated_at", "base_fee", "extra_fees", "paid", "saldo", "visa_requested")
    fieldsets = (
        (None, {"fields": ("event", "user")}),
        (
            "Payment",
            {
                "fields": (
                    ("base_fee", "extra_fees"),
                    "manual_extra_fees",
                    ("paid_via_invoice", "invoice_requested", "invoice_sent"),
                    "coupon",
                    "paid",
                    "saldo",
                ),
            },
        ),
        ("Visum", {"fields": ("visa_requested", "visa_sent")}),
    )
    inlines = (InvitationLetterInline,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user__profile__institution", "coupon")
            .prefetch_related("event")
        )

    def get_form(self, request, obj=None, **kwargs):
        self.instance = obj  # Capture instance before the form gets generated
        return super().get_form(request, obj=obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not self.instance:
            return readonly_fields + ("coupon", "sessions")
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if self.instance and db_field.name == "coupon":
            kwargs["queryset"] = Coupon.objects.filter(event_id=self.instance.event_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if self.instance and db_field.name == "sessions" and self.instance:
            kwargs["queryset"] = Session.objects.filter(event_id=self.instance.event_id)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # custom actions

    def pdf_badges(self, request, queryset):
        maker = BadgesPdfMaker(registrations=queryset, filename="badges.pdf")
        return maker.response

    def send_payment_reminder(self, request, queryset):
        queryset = queryset.exclude(saldo__gte=0)  # check if `registration.saldo` >= 0 (aka `is_paid()`)
        for instance in queryset:
            email = (
                "events.registrations.payment_reminder",
                f"[HiPEAC] Payment reminder #{instance.event.hashtag} / {instance.id}",
                "HiPEAC <management@hipeac.net>",
                [instance.user.email],
                {
                    "user_name": instance.user.profile.name,
                    "event_name": instance.event.name,
                    "registration_id": instance.id,
                    "payment_url": instance.get_payment_url(),
                    "payment_delegated_url": instance.get_payment_delegated_url(),
                    "invoice_requested": instance.invoice_requested,
                },
            )
            send_task("hipeac.tasks.emails.send_from_template", email)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    def send_profile_update_reminder(self, request, queryset):
        user_ids = queryset.values_list("user_id", flat=True)
        users = (
            get_user_model()
            .objects.filter(id__in=user_ids)
            .select_related("profile")
            .prefetch_related("profile__institution")
            .prefetch_related("profile__second_institution")
        )
        send_profile_update_reminders(users)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    def send_reminder(self, request, queryset):
        for instance in queryset:
            email = RegistrationReminderEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    def send_visa_reminder(self, request, queryset):
        queryset = queryset.exclude(visa_requested=False)  # check if `registration.visa_requested` = True
        for instance in queryset:
            email = (
                "events.registrations.visa_reminder",
                f"[HiPEAC] Visa reminder #{instance.event.hashtag} / {instance.id}",
                "HiPEAC <management@hipeac.net>",
                [instance.user.email],
                {
                    "user_name": instance.user.profile.name,
                    "event_name": instance.event.name,
                    "registration_id": instance.id,
                },
            )
            send_task("hipeac.tasks.emails.send_from_template", email)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    pdf_badges.short_description = "ℹ️ Download badges"
    send_payment_reminder.short_description = "➡️ Send payment reminder"
    send_profile_update_reminder.short_description = "➡️ Send profile update reminder"
    send_reminder.short_description = "➡️ Send reminder to users"
    send_visa_reminder.short_description = "➡️ Send visa reminder"

    # custom views

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        extra_context = extra_context or {}
        extra_context["has_letter"] = InvitationLetter.objects.filter(registration_id=object_id).exists()
        extra_context["payment_delegated_url"] = obj.get_payment_delegated_url() if not obj.is_paid else None
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        my_urls = [
            path("<path:object_id>/letter/", self.pdf_letter_view, name="registration_pdf_letter"),
        ]
        return my_urls + super().get_urls()

    def pdf_letter_view(self, request, object_id, extra_context=None):
        from hipeac.site.views.file_makers.pdf import InvitationLetterPdfMaker

        obj = Registration.objects.get(id=object_id)
        maker = InvitationLetterPdfMaker(registration=obj, filename=f"letter--{obj.uuid}.pdf", as_attachment=False)
        return maker.response

    # custom fields

    def fee(self, obj) -> str:
        return format_html(f'<span class="text-nowrap">{obj.base_fee} + {obj.extra_fees}</span>')

    def is_paid(self, obj) -> bool:
        return obj.is_paid

    def name(self, obj):
        institution = obj.user.profile.institution.short_name if obj.user.profile.institution else "-"
        url = reverse("admin:auth_user_changelist")
        return format_html(
            f'<a href="{url}{obj.user_id}/" target="admin_user" class="text-nowrap">{obj.user.profile.name}</a>'
            f", {institution}"
        )

    def invoice(self, obj):
        requested = "yes" if obj.invoice_requested else "no"
        sent = "yes" if obj.invoice_sent else "no"
        return format_html(
            '<span class="text-nowrap">'
            f'<img src="/static/admin/img/icon-{requested}.svg" title="Invoice requested: {requested}">'
            " / "
            f'<img src="/static/admin/img/icon-{sent}.svg" title="Invoice sent: {sent}">'
            "<span>"
        )

    def visa(self, obj):
        requested = "yes" if obj.visa_requested else "no"
        sent = "yes" if obj.visa_sent else "no"
        return format_html(
            '<span class="text-nowrap">'
            f'<img src="/static/admin/img/icon-{requested}.svg" title="Visa requested: {requested}">'
            " / "
            f'<img src="/static/admin/img/icon-{sent}.svg" title="Visa sent: {sent}">'
            "</span>"
        )

    def with_coupon(self, obj):
        return obj.coupon is not None

    is_paid.boolean = True
    is_paid.short_description = "Paid"
    with_coupon.boolean = True
    with_coupon.short_description = "Coupon"
