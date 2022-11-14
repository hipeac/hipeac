from django.contrib import admin
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.urls import reverse
from django.utils.html import format_html

from hipeac.functions import send_task
from hipeac.models.membership import Member, Membership, MembershipRequest
from .csv.users import csv_users_activity
from .files import FilesInline


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    actions = (
        "export_csv_activity",
        "extract_publications_from_dblp",
    )
    date_hierarchy = "date"
    list_display = ("id", "_name", "date", "type", "gender", "institution")
    list_filter = ("type", "gender")
    search_fields = ("name", "email", "institution__country")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("institution", "second_institution")

    # custom fields

    def id(self, obj):
        return obj.user_id

    def _name(self, obj):
        url = reverse("admin:auth_user_changelist")
        return format_html(f'<a href="{url}{obj.user_id}/" target="admin_user" class="text-nowrap">{obj.name}</a>')

    _name.short_description = "Name"

    # custom actions

    @admin.action(description="[CSV] Export activity report for selected users")
    def export_csv_activity(self, request, queryset):
        qs = get_user_model().objects.filter(id__in=queryset.values_list("user_id", flat=True))
        return csv_users_activity(qs, "hipeac-users--activity.csv")

    @admin.action(description="[DATA] Extract publications from DBLP")
    def extract_publications_from_dblp(self, request, queryset):
        for member in queryset:
            send_task("hipeac.tasks.dblp.extract_publications_for_user", (member.user_id,))
        admin.ModelAdmin.message_user(
            self, request, "Publication extraction has started, " "results from DBLP will be available soon."
        )
        return True


class MembershipInline(admin.TabularInline):
    model = Membership
    fk_name = "user"
    classes = ("collapse",)
    extra = 0
    # form
    raw_id_fields = ("advisor",)


def send_members_welcome_email(queryset):
    for instance in queryset:
        email = (
            "users.members.welcome" if instance.membership_type == "member" else "users.members.non_eu.welcome",
            "Welcome to HiPEAC",
            "HiPEAC <membership@hipeac.net>",
            [instance.clean_email, "membership@hipeac.net"],
            {"user_name": instance.name, "is_registered": True if instance.user else False},
        )
        send_task("hipeac.tasks.emails.send_from_template", email)


class MembershipRequestForm(ModelForm):
    class Meta:
        help_texts = {
            "user": "If the proposed member had already a HiPEAC user account, please select his account.",
            "decision_date": 'Required for "Accepted" or "Rejected" membership requests.',
        }


@admin.register(MembershipRequest)
class MembershipRequestAdmin(admin.ModelAdmin):
    actions = ("send_members_welcome",)
    date_hierarchy = "created_at"
    list_display = ("id", "user_name", "affiliation", "accepted", "decision_date")
    list_filter = ("accepted",)
    search_fields = ("name", "affiliation", "email")
    # form
    raw_id_fields = ("user",)
    fieldsets = (
        (None, {"fields": ("name", "affiliation", "email", "user", "membership_type")}),
        ("Request", {"fields": ("website", "motivation")}),
        ("Decision", {"fields": ("accepted", "decision_date", "comments")}),
    )
    inlines = (FilesInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("user__profile")

    # custom actions

    @admin.action(description="➡️ Send welcome email (only if accepted)")
    def send_members_welcome(self, request, queryset):
        queryset = queryset.filter(accepted=True)
        send_members_welcome_email(queryset)
        for membreq in queryset.filter(user__isnull=False):
            Membership.objects.filter(user=membreq.user, revocation_date__isnull=True).update(
                revocation_date=membreq.decision_date
            )
            Membership.objects.create(user=membreq.user, type=Membership.MEMBER, date=membreq.decision_date)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")

    # custom fields

    def user_name(self, obj):
        if obj.user:
            url = reverse("admin:auth_user_changelist")
            return format_html(f'<a href="{url}{obj.user_id}/" target="admin_user">{obj.user.profile.name}</a>')
        return obj.name
