from django.contrib import admin
from django.forms import ModelForm

from hipeac.functions import send_task
from hipeac.models import MembershipRequest


def send_members_welcome(queryset):
    for instance in queryset:
        email = (
            'users.members.welcome',
            'Welcome to HiPEAC',
            'HiPEAC <membership@hipeac.net>',
            ['eneko@illarra.com'],  # [instance.clean_email, 'membership@hipeac.net'],
            {
                'user_name': instance.name,
                'is_registered': True if instance.user else False,
            }
        )
        send_task('hipeac.tasks.emails.send_from_template', email)
    return


class MembershipRequestForm(ModelForm):

    class Meta:
        help_texts = {
            'user': 'If the proposed member had already a HiPEAC user account, please select his account.',
            'decision_date': 'Required for "Accepted" or "Rejected" membership requests.',
        }


@admin.register(MembershipRequest)
class MembershipRequestAdmin(admin.ModelAdmin):
    actions = ('make_accepted', 'make_rejected', 'send_members_welcome',)
    list_display = ('id', 'name', 'affiliation', 'created_at', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'affiliation', 'email')

    raw_id_fields = ('user',)
    fieldsets = (
        (None, {
            'fields': ('name', 'affiliation', 'email', 'user', 'membership_type'),
        }),
        ('REQUEST', {
            'fields': ('website', 'motivation'),
        }),
        ('DECISION', {
            'fields': ('status', 'decision_date', 'comments'),
        }),
    )

    def make_accepted(self, request, queryset):
        queryset.update(status='OK')
    make_accepted.short_description = '[Bulk] Mark as accepted'

    def make_rejected(self, request, queryset):
        queryset.update(status='NO')
    make_rejected.short_description = '[Bulk] Mark as rejected'

    def send_members_welcome(self, request, queryset):
        queryset = queryset.filter(status='OK')
        send_members_welcome(queryset)
        admin.ModelAdmin.message_user(self, request, 'Emails are being sent.')
    send_members_welcome.short_description = ('[Mailer] Send welcome email (only if accepted)')
