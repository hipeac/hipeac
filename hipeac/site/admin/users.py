from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.db.models import Q
from django.forms import ModelForm

from hipeac.forms import ApplicationAreasChoiceField, TopicsChoiceField, MembershipTagsChoiceField
from hipeac.functions import send_task
from hipeac.models import Profile, Institution, Link
from hipeac.tools.csv import ModelCsvWriter
from .generic import LinksInline


admin.site.unregister(get_user_model())


def send_profile_update_reminders(queryset):
    for instance in queryset:
        profile = instance.profile
        email = (
            'users.profile.update_reminder',
            'Update your HiPEAC profile: affiliation, research interests',
            'HiPEAC <management@hipeac.net>',
            [instance.email],
            {
                'username': instance.username,
                'user_name': profile.name,
                'institution': profile.institution.name if profile.institution else '(none)',
                'second_institution': profile.second_institution.name if profile.second_institution else '(none)',
                'topics': profile.get_metadata_display('topics') if profile.topics != '' else '(none)',
            }
        )
        send_task('hipeac.tasks.emails.send_from_template', email)
    return


class ProfileCsvWriter(ModelCsvWriter):
    model = Profile
    custom_fields = ('username', 'name', 'email')
    exclude = ('user', 'bio', 'title', 'department', 'links', 'projects', 'publications', 'is_bouncing', 'updated_at')

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related('gender', 'meal_preference', 'position', 'advisor',
                                         'institution', 'second_institution')


class ProfileAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField(required=False)
    topics = TopicsChoiceField(required=False)
    membership_tags = MembershipTagsChoiceField(required=False)


class ProfileInline(admin.StackedInline):
    model = Profile
    fk_name = 'user'
    form = ProfileAdminForm
    exclude = ('is_bouncing',)

    autocomplete_fields = ('institution', 'second_institution', 'projects')
    raw_id_fields = ('advisor',)
    inlines = (LinksInline,)
    fieldsets = (
        (None, {
            'fields': ('country', 'bio', 'meal_preference', 'image'),
        }),
        ('AFFILIATION', {
            'fields': ('position', 'institution', 'department', 'second_institution'),
        }),
        ('MEMBERSHIP', {
            'fields': (('membership_date', 'membership_revocation_date'), 'advisor', 'membership_tags'),
        }),
        ('METADATA', {
            'classes': ('collapse',),
            'fields': ('application_areas', 'topics', 'projects'),
        }),
        ('PRIVACY', {
            'classes': ('collapse',),
            'fields': ('is_subscribed', 'is_public'),
        }),
    )


class MembershipTypeFilter(admin.SimpleListFilter):
    title = 'membership'
    parameter_name = 'membership'

    def lookups(self, request, model_admin):
        return (
            ('any', 'All members'),
            ('member', 'Member'),
            ('affiliated', 'Affiliated member'),
            ('industry', 'Industry member or affiliate'),
            ('innovation', 'Innovation member'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        queryset = queryset.filter(is_active=True, profile__membership_revocation_date__isnull=True)

        if value in ['any', 'industry']:
            queryset = queryset.filter(
                Q(profile__membership_tags__contains='member') |
                Q(profile__membership_tags__contains='affiliated')
            )

        if value:
            if value == 'any':
                return queryset
            elif value == 'industry':
                return queryset.filter(
                    Q(profile__institution__type__in=[Institution.INDUSTRY, Institution.SME]) |
                    Q(profile__second_institution__type__in=[Institution.INDUSTRY, Institution.SME])
                )
            elif value != '':
                return queryset.filter(profile__membership_tags__contains=value)


@admin.register(get_user_model())
class UserAdmin(AuthUserAdmin):
    actions = ('send_profile_update_reminder', 'select_export_users_csv', 'extract_publications_from_dblp')
    list_display = ('id', 'username', 'name', 'institution', 'email', 'membership_tags')
    list_filter = (MembershipTypeFilter,) + AuthUserAdmin.list_filter
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__institution__name')

    inlines = (ProfileInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile').prefetch_related('profile__institution')

    def membership_tags(self, obj) -> str:
        return obj.profile.membership_tags

    def name(self, obj) -> str:
        return obj.profile.name

    def institution(self, obj) -> str:
        return obj.profile.institution

    def send_profile_update_reminder(self, request, queryset):
        queryset = queryset.prefetch_related('profile__second_institution')
        send_profile_update_reminders(queryset)
        admin.ModelAdmin.message_user(self, request, 'Emails are being sent.')
    send_profile_update_reminder.short_description = ('[Mailer] Send profile update reminder')

    def select_export_users_csv(self, request, queryset):
        ids = queryset.values_list('id', flat=True)
        return ProfileCsvWriter(filename='hipeac-users.csv', queryset=Profile.objects.filter(user_id__in=ids)).response
    select_export_users_csv.short_description = '[CSV] Export users\' data'

    def extract_publications_from_dblp(self, request, queryset):
        for user in queryset:
            send_task('hipeac.tasks.dblp.extract_publications_for_user', (user.id,))
        admin.ModelAdmin.message_user(self, request, 'Publication extraction has started, '
                                                     'results from DBLP will be available soon.')
        return True
    extract_publications_from_dblp.short_description = '[DATA] Extract publications from DBLP'
