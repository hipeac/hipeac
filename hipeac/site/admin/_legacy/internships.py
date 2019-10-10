from django.contrib import admin

from hipeac.models._legacy.internships import InternshipCall, Internship, InternshipApplication


@admin.register(InternshipCall)
class InternshipCallAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date', 'application_deadline', 'is_frozen')


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'institution', 'location', 'country')
    list_filter = ('call',)

    autocomplete_fields = ('institution',)
    raw_id_fields = ('call',)


@admin.register(InternshipApplication)
class InternshipApplicationAdmin(admin.ModelAdmin):
    date_hierarchy = 'internship__call__start_date'
    list_display = ('id', 'internship', 'status', 'selected')
    search_fields = ('created_by__first_name', 'created_by__last_name',
                     'internship__title', 'internship__institution__name')

    raw_id_fields = ('internship', 'created_by')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('internship__call', 'internship__institution') \
                                            .prefetch_related('created_by__profile')
