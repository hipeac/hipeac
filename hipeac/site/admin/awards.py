from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe

from hipeac.functions import send_task
from hipeac.models import PublicationConference, TechTransferCall, TechTransferApplication


@admin.register(PublicationConference)
class PublicationConferenceAdmin(admin.ModelAdmin):
    actions = ('extract_publications_from_dblp',)
    list_display = ('id', 'name')
    list_filter = ('year',)

    def name(self, obj):
        return str(obj)

    def extract_publications_from_dblp(self, request, queryset):
        for conference in queryset:
            send_task('hipeac.tasks.dblp.extract_publications_for_conference', (conference.id,))
        admin.ModelAdmin.message_user(self, request, 'Publication extraction has started, '
                                                     'results from DBLP will be available soon.')
        return True
    extract_publications_from_dblp.short_description = '[DATA] Extract publications from DBLP'


@admin.register(TechTransferCall)
class TechTransferCallAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date', 'end_date', 'applications_link', 'is_active')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(Count('applications'))

    def applications_link(self, obj):
        if obj.applications__count == 0:
            return '-'
        url = reverse('admin:hipeac_techtransferapplication_changelist')
        return mark_safe(f'<a href="{url}?call__id__exact={obj.id}">{obj.applications__count}</a>')
    applications_link.short_description = 'Applications'


@admin.register(TechTransferApplication)
class TechTransferApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'awarded', 'awardee')
    list_filter = ('call', 'awarded')

    raw_id_fields = ('applicant', 'team', 'awardee', 'awarded_from', 'awarded_to')

    fieldsets = (
        (None, {
            'fields': ('call', 'applicant', 'awarded'),
        }),
        ('Application details', {
            'fields': ('title', 'description', 'partners_description', 'value'),
        }),
        ('Awards', {
            'fields': ('team', 'awardee', 'awarded_summary', 'awarded_from', 'awarded_to'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('awardee')
