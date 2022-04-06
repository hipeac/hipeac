from django.contrib import admin
from django.db import models
from django.urls import path
from typing import Optional

from hipeac.models.events import Event
from hipeac.models.recruitment import PhdMobility, Job, JobEvaluation
from hipeac.site.pdfs.recruitment import JobsPdfMaker
from .generic import custom_titled_filter
from .links import LinksInline
from .metadata import ApplicationAreasInline, TopicsInline
from .widgets import MarkdownEditorWidget


@admin.register(PhdMobility)
class PhdMobilityAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "start_date", "end_date", "title")
    list_filter = ("type", "start_date")
    date_hierarchy = "start_date"
    # form
    raw_id_fields = ("student", "institution", "job")
    inlines = (ApplicationAreasInline, TopicsInline)


class JobEvaluationInline(admin.StackedInline):
    model = JobEvaluation
    verbose_name_plural = "Job evaluation"
    extra = 0

    raw_id_fields = ("selected_user",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = (
        "id",
        "title",
        "institution_name",
        "employment_type",
        "deadline",
        "created_at",
        "positive_evaluation",
    )
    list_filter = (("evaluation__value", custom_titled_filter("evaluation")), "employment_type", "deadline")
    search_fields = ("title", "institution__name")
    # form
    autocomplete_fields = ("career_levels",)
    raw_id_fields = ("institution", "project", "created_by")
    fieldsets = (
        (None, {"fields": ("created_by", "title", "institution", "project")}),
        (
            "Information",
            {
                "fields": (
                    ("country", "location"),
                    "description",
                    "employment_type",
                    "positions",
                    "deadline",
                    "career_levels",
                    "add_to_euraxess",
                ),
            },
        ),
        ("Contact", {"fields": ("email",)}),
    )
    inlines = (ApplicationAreasInline, TopicsInline, LinksInline, JobEvaluationInline)
    formfield_overrides = {
        models.TextField: {"widget": MarkdownEditorWidget},
    }

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("institution", "employment_type")
            .select_related("evaluation")
        )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return ("created_by",)

    # custom views

    def get_urls(self):
        my_urls = [
            path("pdf/", self.pdf_current_jobs, name="recruitment_pdf_current_jobs"),
            path("pdf/upcoming/", self.pdf_upcoming_event_jobs, name="recruitment_pdf_upcoming_event_jobs"),
        ]
        return my_urls + super().get_urls()

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

    # custom fields

    def evaluated(self, obj) -> bool:
        return obj.evaluation is not None

    def institution_name(self, obj) -> str:
        return obj.institution.short_name

    def positive_evaluation(self, obj) -> Optional[bool]:
        return {
            None: None,
            JobEvaluation.NO: False,
            JobEvaluation.YES: True,
            JobEvaluation.YES_HIPEAC: True,
        }[obj.evaluation.value]

    evaluated.boolean = True
    evaluated.short_description = "Evaluated"
    positive_evaluation.boolean = True
    positive_evaluation.short_description = "Evaluation"
