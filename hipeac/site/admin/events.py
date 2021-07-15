from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.forms import ModelForm
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from hipeac.forms import ApplicationAreasChoiceField, TopicsChoiceField
from hipeac.functions import send_task
from hipeac.models import (
    Profile,
    Event,
    Committee,
    Coupon,
    Registration,
    Roadshow,
    Break,
    Session,
    Sponsor,
    Venue,
    Poster,
    Room,
    SessionProposal,
    Course,
    CourseSession,
)
from hipeac.site.emails.events import (
    AcacesPosterAbstractsReminderEmail,
    RegistrationReminderEmail,
    SessionProceedingsEmail,
    SessionReminderEmail,
    SessionSpeakersReminderEmail,
    NoShowsEmail,
)
from .csv.events import csv_zoom_attendee_report
from .generic import ImagesInline, LinksInline, PermissionsInline, PrivateFilesInline
from .users import ProfileCsvWriter, send_profile_update_reminders


class BreaksInline(admin.TabularInline):
    model = Break
    classes = ("collapse",)
    extra = 0


class CommitteesInline(admin.TabularInline):
    autocomplete_fields = ("members",)
    classes = ("collapse",)
    model = Committee
    extra = 0


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "value", "notes")
    list_filter = ("event",)
    search_fields = ("code", "notes")


class CouponsInline(admin.TabularInline):
    model = Coupon
    classes = ("collapse",)
    extra = 0


class PostersInline(admin.StackedInline):
    classes = ("collapse",)
    model = Poster
    extra = 0


class SponsorsInline(admin.TabularInline):
    model = Sponsor
    classes = ("collapse",)
    extra = 0
    raw_id_fields = ("institution", "project")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    actions = ("select_export_users_csv", "select_zoom_attendee_report_csv", "sync_webinar_registrants")
    date_hierarchy = "start_date"
    list_display = (
        "id",
        "start_date",
        "end_date",
        "name",
        "type",
        "sessions_link",
        "registrations_link",
        "is_active",
        "is_open",
    )
    list_filter = ("type",)
    list_per_page = 20
    search_fields = ("city", "country", "start_date__year")

    autocomplete_fields = ("coordinating_institution", "venues")
    readonly_fields = ("registrations_count",)
    fieldsets = (
        (
            None,
            {"fields": ("is_virtual", "city", "country", "coordinating_institution", "hashtag", "registrations_count")},
        ),
        (
            "DATES",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "registration_start_date",
                    ("registration_early_deadline", "registration_deadline"),
                ),
            },
        ),
        ("INFORMATION", {"fields": ("presentation", "venues", "logistics")}),
        ("IMAGES", {"fields": ("image",)}),
    )
    inlines = (
        BreaksInline,
        SponsorsInline,
        CommitteesInline,
        CouponsInline,
        LinksInline,
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(Count("sessions", distinct=True))
            .annotate(Count("registrations", distinct=True))
        )

    def is_active(self, obj) -> bool:
        return obj.is_active()

    is_active.boolean = True
    is_active.short_description = "Active"

    def is_open(self, obj) -> bool:
        return obj.is_open_for_registration()

    is_open.boolean = True
    is_open.short_description = "Open"

    def registrations_link(self, obj):
        if obj.registrations__count == 0:
            return "-"
        url = reverse("admin:hipeac_registration_changelist")
        return mark_safe(f'<a href="{url}?event__id__exact={obj.id}">{obj.registrations__count}</a>')

    registrations_link.short_description = "Registrations"

    def sessions_link(self, obj):
        if obj.sessions__count == 0:
            return "-"
        url = reverse("admin:hipeac_session_changelist")
        return mark_safe(f'<a href="{url}?event__id__exact={obj.id}">{obj.sessions__count}</a>')

    sessions_link.short_description = "Sessions"

    def select_export_users_csv(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "Please select only one event.")
            return

        ids = queryset.first().registrations.values_list("user_id", flat=True)
        return ProfileCsvWriter(filename="hipeac-jobs.csv", queryset=Profile.objects.filter(user_id__in=ids)).response

    select_export_users_csv.short_description = "[CSV] Export attendees data for an event"

    def select_zoom_attendee_report_csv(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "Please select only one event.")
            return

        return csv_zoom_attendee_report(queryset.first(), "hipeac-events--zoom-attendee-report.csv")

    select_zoom_attendee_report_csv.short_description = "[Zoom] Export attendees report (CSV)"

    def sync_webinar_registrants(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "Please select only one event.")
            return

        send_task("hipeac.tasks.events.sync_webinar_registrants", (queryset.first().id,))
        messages.info(request, "Attendees information is being synced with Zoom.")
        return

    sync_webinar_registrants.short_description = "[Zoom] Sync webinar attendees"


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


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = (
        "id",
        "created_at",
        "name",
        "fee",
        "is_paid",
        "with_coupon",
        "invoice_requested",
        "invoice_sent",
        "visa_requested",
        "visa_sent",
    )
    list_filter = (
        RegistrationIsPaidFilter,
        "invoice_requested",
        "invoice_sent",
        "with_booth",
        "visa_requested",
        "visa_sent",
        "status",
        "event",
    )
    search_fields = ("id", "user__email", "user__username", "user__first_name", "user__last_name")

    autocomplete_fields = ("event",)
    inlines = (PostersInline,)
    raw_id_fields = ("user", "coupon")
    readonly_fields = ("base_fee", "extra_fees", "paid", "saldo")
    fieldsets = (
        (None, {"fields": ("event", ("user", "visa_requested", "visa_sent"))}),
        (
            "PAYMENT",
            {
                "fields": (
                    "fee_type",
                    ("base_fee", "extra_fees"),
                    "manual_extra_fees",
                    ("paid_via_invoice", "invoice_requested", "invoice_sent"),
                    "coupon",
                    "paid",
                    "saldo",
                ),
            },
        ),
        ("EXTRA INFORMATION", {"fields": ("with_booth",)}),
    )
    actions = (
        "send_reminder",
        "send_payment_reminder",
        "send_profile_update_reminder",
        "send_no_show_reminder",
        "send_acaces_poster_abstract_reminder",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user__profile__institution", "coupon")
            .prefetch_related("event")
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        instance = Registration.objects.get(pk=object_id)
        extra_context = extra_context or {}
        extra_context["is_paid"] = instance.is_paid
        extra_context["base_fee"] = instance.base_fee
        extra_context["remaining_fee"] = instance.remaining_fee
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def name(self, obj):
        institution = obj.user.profile.institution.short_name if obj.user.profile.institution else "-"
        url = reverse("admin:auth_user_changelist")
        return format_html(
            f'<a href="{url}{obj.user_id}/" target="admin_user">{obj.user.profile.name}</a>, {institution}'
        )

    def fee(self, obj):
        return format_html(f"{obj.base_fee}&nbsp;+&nbsp;{obj.extra_fees}")

    def is_paid(self, obj) -> bool:
        return obj.is_paid

    is_paid.boolean = True
    is_paid.short_description = "Paid"

    def with_coupon(self, obj):
        return obj.coupon is not None

    with_coupon.boolean = True
    with_coupon.short_description = "Coupon"

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
                    "invoice_requested": instance.invoice_requested,
                },
            )
            send_task("hipeac.tasks.emails.send_from_template", email)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    send_payment_reminder.short_description = "[Mailer] Send payment reminder"

    def send_no_show_reminder(self, request, queryset):
        for instance in queryset:
            email = NoShowsEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    send_no_show_reminder.short_description = "[Mailer] Send no-shows reminder to users"

    def send_reminder(self, request, queryset):
        for instance in queryset:
            email = RegistrationReminderEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    send_reminder.short_description = "[Mailer] Send reminder to users"

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

    send_profile_update_reminder.short_description = "[Mailer] Send profile update reminder"

    def send_acaces_poster_abstract_reminder(self, request, queryset):
        for instance in queryset:
            email = AcacesPosterAbstractsReminderEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    send_acaces_poster_abstract_reminder.short_description = "[Mailer] Send ACACES poster reminder to users"


@admin.register(Roadshow)
class RoadshowAdmin(admin.ModelAdmin):
    date_hierarchy = "start_date"
    list_display = ("id", "name", "country", "start_date", "end_date")

    inlines = (ImagesInline, LinksInline)


class SessionAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField(required=False)
    topics = TopicsChoiceField(required=False)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    form = SessionAdminForm

    actions = ("select_export_users_csv", "send_reminder", "send_speakers_reminder", "send_proceedings_reminder")
    list_display = ("id", "title", "start_at", "end_at", "session_type", "registrations_count")
    list_filter = ("session_type", "event")
    search_fields = ("title",)

    autocomplete_fields = ("event", "projects", "main_speaker", "speakers", "room")
    radio_fields = {"session_type": admin.VERTICAL}
    inlines = (LinksInline, PrivateFilesInline, PermissionsInline)
    fieldsets = (
        (None, {"fields": ("event", ("start_at", "end_at"), "room", "session_type", "title", "is_private")}),
        ("INFO", {"fields": ("main_speaker", "speakers", "summary", "program", "projects", "organizers")}),
        ("ZOOM", {"fields": ("zoom_webinar_id", "zoom_attendee_report")}),
        ("METADATA", {"classes": ("collapse",), "fields": ("application_areas", "topics")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("event", "session_type")
            .annotate(Count("registrations", distinct=True))
        )

    def registrations_count(self, obj):
        return obj.registrations__count if obj.registrations__count > 0 else "-"

    registrations_count.short_description = "Registrations"

    def select_export_users_csv(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "Please select only one session.")
            return

        ids = queryset.first().registrations.values_list("user_id", flat=True)
        return ProfileCsvWriter(filename="hipeac-jobs.csv", queryset=Profile.objects.filter(user_id__in=ids)).response

    select_export_users_csv.short_description = "[CSV] Export attendees data for a session"

    def send_proceedings_reminder(self, request, queryset):
        for instance in queryset:
            if instance.acl.count() == 0:
                continue
            email = SessionProceedingsEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    send_proceedings_reminder.short_description = "[Mailer] Ask proceedings to organizers"

    def send_reminder(self, request, queryset):
        for instance in queryset:
            if instance.acl.count() == 0:
                continue
            email = SessionReminderEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    send_reminder.short_description = "[Mailer] Send reminder to organizers"

    def send_speakers_reminder(self, request, queryset):
        for instance in queryset:
            if instance.acl.count() == 0:
                continue
            email = SessionSpeakersReminderEmail(instance=instance)
            send_task("hipeac.tasks.emails.send_from_template", email.data)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    send_speakers_reminder.short_description = "[Mailer] Send speakers reminder to organizers"


class RoomsInline(admin.TabularInline):
    model = Room
    extra = 0


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "country")
    search_fields = ("name", "city", "country")

    inlines = (ImagesInline, LinksInline)


class SessionProposalAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField(required=False)
    topics = TopicsChoiceField(required=False)


@admin.register(SessionProposal)
class SessionProposalAdmin(admin.ModelAdmin):
    form = SessionProposalAdminForm

    date_hierarchy = "created_at"
    list_display = ("id", "event", "title", "created_by", "created_at", "link")
    list_filter = ("event",)
    search_fields = ("uuid", "first_name", "last_name")

    def created_by(self, obj):
        return f"{obj.first_name} {obj.last_name} <{obj.email}>"

    def link(self, obj):
        return mark_safe(f'<a class="viewlink" href="{obj.get_absolute_url()}" target="_blank"></a>')

    link.short_description = "View"


class CourseSessionsInline(admin.TabularInline):
    model = CourseSession
    extra = 0


class CourseAdminForm(ModelForm):
    topics = TopicsChoiceField(required=False)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm

    search_fields = ("name",)

    raw_id_fields = ("teachers",)
    inlines = (CourseSessionsInline, LinksInline, PrivateFilesInline)
