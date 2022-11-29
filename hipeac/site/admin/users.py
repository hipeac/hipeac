from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.functions import send_task
from hipeac.models import Profile, RelatedUser
from hipeac.tools.csv import ModelCsvWriter
from .membership import MembershipInline


admin.site.unregister(get_user_model())


def send_profile_update_reminders(queryset):
    for instance in queryset:
        profile = instance.profile
        email = (
            "users.profile.update_reminder",
            "Update your HiPEAC profile: affiliation, research interests",
            "HiPEAC <management@hipeac.net>",
            [instance.email],
            {
                "username": instance.username,
                "user_name": profile.name,
                "institution": profile.institution.name if profile.institution else "(none)",
                "second_institution": profile.second_institution.name if profile.second_institution else "(none)",
                "topics": profile.get_topics_display(),
            },
        )
        send_task("hipeac.tasks.emails.send_from_template", email)


class ProfileCsvWriter(ModelCsvWriter):
    model = Profile
    custom_fields = ("username", "name", "email")
    exclude = ("user", "bio", "title", "department", "links", "projects", "publications", "is_bouncing", "updated_at")

    def get_queryset(self, queryset):
        return queryset.prefetch_related("gender", "meal_preference", "position", "institution", "second_institution")


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    classes = ("collapse",)
    # form
    raw_id_fields = ("institution", "second_institution")


@admin.register(get_user_model())
class UserAdmin(AuthUserAdmin):
    actions = (
        "send_profile_update_reminder",
        "export_users_csv",
        "extract_publications_from_dblp",
    )
    list_display = ("id", "username", "name", "institution", "email")
    # list_filter = (MembershipTypeFilter,) + AuthUserAdmin.list_filter
    list_filter = AuthUserAdmin.list_filter
    search_fields = ("username", "email", "first_name", "last_name", "profile__institution__name")

    inlines = (ProfileInline, MembershipInline)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("profile").prefetch_related("profile__institution")

    # custom fields

    def name(self, obj) -> str:
        return obj.profile.name

    def institution(self, obj) -> str:
        return obj.profile.institution

    # custom actions

    @admin.action(description="[CSV] Export users' data")
    def export_users_csv(self, request, queryset):
        ids = queryset.values_list("id", flat=True)
        return ProfileCsvWriter(filename="hipeac-users.csv", queryset=Profile.objects.filter(user_id__in=ids)).response

    @admin.action(description="[DATA] Extract publications from DBLP")
    def extract_publications_from_dblp(self, request, queryset):
        for user in queryset:
            send_task("hipeac.tasks.dblp.extract_publications_for_user", (user.id,))
        admin.ModelAdmin.message_user(
            self, request, "Publication extraction has started, " "results from DBLP will be available soon."
        )
        return True

    @admin.action(description="➡️ Send profile update reminder")
    def send_profile_update_reminder(self, request, queryset):
        queryset = queryset.prefetch_related("profile__second_institution")
        send_profile_update_reminders(queryset)
        admin.ModelAdmin.message_user(self, request, "Emails are being sent.")


class UsersInline(GenericTabularInline):
    model = RelatedUser
    classes = ("collapse",)
    extra = 0
    verbose_name = "user"
    # form
    raw_id_fields = ("user",)


class ManagersInline(UsersInline):
    verbose_name = "manager"


class MembersInline(UsersInline):
    verbose_name = "member"


class OwnersInline(UsersInline):
    verbose_name = "owner"


class SpeakersInline(UsersInline):
    verbose_name = "speaker"


class TeachersInline(UsersInline):
    verbose_name = "teacher"


class TeamMemberInline(UsersInline):
    verbose_name = "team member"
