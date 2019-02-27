from django.contrib import admin

from hipeac.functions import send_task
from hipeac.models import PublicationConference


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
