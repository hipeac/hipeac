from django.contrib import admin
from django.forms import ModelForm
from django.urls import path
from django.utils import timezone

from hipeac.forms import ApplicationAreasChoiceField, JobPositionChoiceField, TopicsChoiceField
from hipeac.models import Metadata, Job
from hipeac.site.views import JobsPdfMaker
from .generic import HideDeleteActionMixin, LinksInline, PermissionsInline


class JobAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField()
    career_levels = JobPositionChoiceField()
    topics = TopicsChoiceField()


@admin.register(Job)
class JobAdmin(HideDeleteActionMixin, admin.ModelAdmin):
    form = JobAdminForm
    exclude = ['updated_at']

    actions = ('select_export_pdf', 'select_export_csv')
    date_hierarchy = 'created_at'
    list_display = ('id', 'title', 'institution', 'employment_type', 'deadline', 'created_at')
    list_filter = ('employment_type', 'deadline', 'created_at', 'country',)
    search_fields = ('title', 'institution__name')

    autocomplete_fields = ('institution', 'project')
    radio_fields = {'employment_type': admin.VERTICAL}
    inlines = [LinksInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'institution', 'project'),
        }),
        ('INFO', {
            'fields': (('country', 'location'), 'description', 'employment_type', 'positions', 'deadline'),
        }),
        ('CONTACT', {
            'fields': ('email',),
        }),
        ('METADATA', {
            'classes': ('collapse',),
            'fields': ('career_levels', 'application_areas', 'topics'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('institution', 'employment_type')

    def get_urls(self):
        my_urls = [
            path('pdf/', self.pdf_current_jobs, name='recruitment_pdf_current_jobs')
        ]
        return my_urls + super().get_urls()

    def pdf_response(self, jobs, as_attachment=True):
        maker = JobsPdfMaker(jobs=jobs, filename='hipeac-jobs.pdf', as_attachment=as_attachment)
        return maker.response

    def pdf_current_jobs(self, request):
        jobs = Job.objects.filter(deadline__gte=timezone.now().date()).order_by('institution__name', 'deadline')
        return self.pdf_response(jobs, False)

    def select_export_pdf(self, request, queryset):
        return self.pdf_response(queryset, False)
    select_export_pdf.short_description = ('[PDF] Generate printable document for selected jobs')

    def select_export_csv(self, request, queryset):
        pass
        # return csv_jobs(queryset)
    select_export_csv.short_description = '[CSV] Export detailed data for selected jobs'
