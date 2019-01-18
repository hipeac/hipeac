from django.contrib import admin
from django.forms import ModelForm
from django.urls import path

from hipeac.forms import ApplicationAreasChoiceField, JobPositionChoiceField, TopicsChoiceField
from hipeac.models import Job, JobEvaluation, Event
from hipeac.site.pdfs.recruitment import JobsPdfMaker
from hipeac.tools.csv import ModelCsvWriter
from .generic import HideDeleteActionMixin, LinksInline, custom_titled_filter


class JobCsvWriter(ModelCsvWriter):
    model = Job
    exclude = ('description', 'links', 'jobevaluation')
    metadata_fields = ('application_areas', 'career_levels', 'topics')


class JobEvaluationInline(admin.StackedInline):
    model = JobEvaluation
    verbose_name_plural = 'Job evaluation'
    extra = 0


class JobAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField(required=False)
    career_levels = JobPositionChoiceField(required=False)
    topics = TopicsChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].required = True


@admin.register(Job)
class JobAdmin(HideDeleteActionMixin, admin.ModelAdmin):
    form = JobAdminForm
    exclude = ('updated_at',)

    actions = ('select_export_pdf', 'select_export_csv')
    date_hierarchy = 'created_at'
    list_display = ('id', 'title', 'institution', 'employment_type', 'deadline', 'created_at')
    list_filter = (('jobevaluation__value', custom_titled_filter('evaluation')),
                   'employment_type', 'deadline', 'created_at', 'country')
    search_fields = ('title', 'institution__name')

    autocomplete_fields = ('institution', 'project')
    radio_fields = {'employment_type': admin.VERTICAL}
    raw_id_fields = ('created_by',)
    inlines = [LinksInline, JobEvaluationInline]
    fieldsets = (
        (None, {
            'fields': ('created_by', 'title', 'institution', 'project'),
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
            path('pdf/', self.pdf_current_jobs, name='recruitment_pdf_current_jobs'),
            path('pdf/upcoming/', self.pdf_upcoming_event_jobs, name='recruitment_pdf_upcoming_event_jobs'),
        ]
        return my_urls + super().get_urls()

    def pdf_response(self, jobs, filename: str = 'hipeac--jobs.pdf', as_attachment: bool = False):
        maker = JobsPdfMaker(jobs=jobs, filename=filename, as_attachment=as_attachment)
        return maker.response

    def pdf_current_jobs(self, request):
        jobs = Job.objects.active().order_by('institution__name', 'deadline')
        return self.pdf_response(jobs)

    def pdf_upcoming_event_jobs(self, request):
        upcoming_event = Event.objects.upcoming()
        jobs = upcoming_event.jobs.order_by('institution__name', 'deadline')
        return self.pdf_response(jobs, f'{upcoming_event.slug}-{upcoming_event.year}--jobs.pdf')

    def select_export_pdf(self, request, queryset):
        return self.pdf_response(queryset)
    select_export_pdf.short_description = ('[PDF] Generate printable document for selected jobs')

    def select_export_csv(self, request, queryset):
        return JobCsvWriter(filename='hipeac-jobs.csv', queryset=queryset).response
    select_export_csv.short_description = '[CSV] Export detailed data for selected jobs'
