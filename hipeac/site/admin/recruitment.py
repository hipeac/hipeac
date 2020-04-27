from django.contrib import admin
from django.forms import ModelForm
from django.urls import path

from hipeac.forms import ApplicationAreasChoiceField, JobPositionChoiceField, TopicsChoiceField
from hipeac.models import PhdMobility, Job, JobEvaluation, Event
from hipeac.site.pdfs.recruitment import JobsPdfMaker
from .csv.recruitment import JobCsvWriter, csv_keywords_analysis
from .generic import HideDeleteActionMixin, LinksInline, custom_titled_filter


@admin.register(PhdMobility)
class PhdMobility(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ("id", "type", "start_date", "title", "student")

    autocomplete_fields = ("institution",)
    raw_id_fields = ("student", "job", "internship")


class JobEvaluationInline(admin.StackedInline):
    model = JobEvaluation
    verbose_name_plural = "Job evaluation"
    extra = 0

    raw_id_fields = ("selected_user",)


class JobAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField(required=False)
    career_levels = JobPositionChoiceField(required=False)
    topics = TopicsChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["add_to_euraxess"].label = "Add to EURAXESS"
        self.fields["created_by"].required = True


@admin.register(Job)
class JobAdmin(HideDeleteActionMixin, admin.ModelAdmin):
    form = JobAdminForm
    exclude = ("updated_at",)

    actions = ("export_pdf", "export_csv", "export_csv_keywords")
    date_hierarchy = "created_at"
    list_display = ("id", "title", "institution", "employment_type", "deadline", "created_at", "evaluated")
    list_filter = (
        ("evaluation__value", custom_titled_filter("evaluation")),
        "employment_type",
        "deadline",
        "created_at",
        "institution__type",
        "country",
    )
    search_fields = ("title", "institution__name", "keywords", "description")

    autocomplete_fields = ("institution", "project")
    radio_fields = {"employment_type": admin.VERTICAL}
    raw_id_fields = ("created_by",)
    inlines = (LinksInline, JobEvaluationInline)
    fieldsets = (
        (None, {"fields": ("created_by", "title", "institution", "project")}),
        (
            "INFO",
            {
                "fields": (
                    ("country", "location"),
                    "description",
                    "employment_type",
                    "positions",
                    "deadline",
                    "add_to_euraxess",
                ),
            },
        ),
        ("CONTACT", {"fields": ("email",)}),
        ("METADATA", {"classes": ("collapse",), "fields": ("career_levels", "application_areas", "topics")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("institution", "employment_type")
            .select_related("evaluation")
        )

    def get_urls(self):
        my_urls = [
            path("pdf/", self.pdf_current_jobs, name="recruitment_pdf_current_jobs"),
            path("pdf/upcoming/", self.pdf_upcoming_event_jobs, name="recruitment_pdf_upcoming_event_jobs"),
        ]
        return my_urls + super().get_urls()

    def evaluated(self, obj) -> bool:
        return obj.evaluation is not None

    evaluated.boolean = True
    evaluated.short_description = "Evaluated"

    def pdf_response(self, jobs, filename: str = "hipeac--jobs.pdf", as_attachment: bool = False):
        maker = JobsPdfMaker(jobs=jobs, filename=filename, as_attachment=as_attachment)
        return maker.response

    def pdf_current_jobs(self, request):
        jobs = Job.objects.active().order_by("institution__name", "deadline")
        return self.pdf_response(jobs)

    def pdf_upcoming_event_jobs(self, request):
        upcoming_event = Event.objects.upcoming()
        jobs = upcoming_event.jobs.order_by("institution__name", "deadline")
        return self.pdf_response(jobs, f"{upcoming_event.slug}-{upcoming_event.year}--jobs.pdf")

    def export_pdf(self, request, queryset):
        return self.pdf_response(queryset)

    export_pdf.short_description = "[PDF] Generate printable document for selected jobs"

    def export_csv(self, request, queryset):
        return JobCsvWriter(filename="hipeac-jobs.csv", queryset=queryset).response

    export_csv.short_description = "[CSV] Export detailed data for selected jobs"

    def export_csv_keywords(self, request, queryset):
        return csv_keywords_analysis(queryset, "hipeac-jobs--keywords.csv")

    export_csv_keywords.short_description = "[CSV] Export keywords for selected jobs"
