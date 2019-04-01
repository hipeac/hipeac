from django.contrib import admin
from django.forms import ModelForm
from django.urls import reverse
from django.utils.html import format_html

from hipeac.functions import send_task
from hipeac.models import MembershipRequest
from .generic import PrivateFilesInline


def send_members_welcome(queryset):
    for instance in queryset:
        email = (
            'users.members.welcome' if instance.membership_type == 'member' else 'users.members.non_eu.welcome',
            'Welcome to HiPEAC',
            'HiPEAC <membership@hipeac.net>',
            [instance.clean_email, 'membership@hipeac.net'],
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
    actions = ('make_rejected', 'send_members_welcome',)
    date_hierarchy = 'created_at'
    list_display = ('id', 'user_name', 'affiliation', 'accepted', 'decision_date')
    list_filter = ('accepted',)
    search_fields = ('name', 'affiliation', 'email')

    inlines = (PrivateFilesInline,)
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {
            'fields': ('name', 'affiliation', 'email', 'user', 'membership_type'),
        }),
        ('REQUEST', {
            'fields': ('website', 'motivation'),
        }),
        ('DECISION', {
            'fields': ('accepted', 'decision_date', 'comments'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('user__profile')

    def user_name(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_changelist')
            return format_html(
                f'<a href="{url}{obj.user_id}/" target="admin_user">{obj.user.profile.name}</a>'
            )
        return obj.name

    def make_rejected(self, request, queryset):
        queryset.update(accepted=False)
    make_rejected.short_description = '[Bulk] Mark as rejected'

    def send_members_welcome(self, request, queryset):
        queryset = queryset.filter(accepted=True)
        send_members_welcome(queryset)
        for membr in queryset.all():
            if membr.user:
                membr.user.profile.membership_tags = membr.membership_type
                membr.user.profile.membership_date = membr.decision_date
                membr.user.profile.save()
        admin.ModelAdmin.message_user(self, request, 'Emails are being sent.')
    send_members_welcome.short_description = ('[Mailer] Send welcome email (only if accepted)')
