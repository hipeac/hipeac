from typing import Optional

from django.contrib import admin
from django.db import models
from django.urls import path, reverse
from django.utils.html import format_html

from hipeac.models.events import Event
from hipeac.models.recruitment import Job, JobEvaluation, JobFair, JobFairCompany, JobFairRegistration, PhdMobility
from hipeac.site.pdfs.recruitment import JobsPdfMaker
from hipeac.site.pdfs.redux.events.badges import JobFairBadgesPdfMaker

from .generic import custom_titled_filter
from .institutions import InstitutionsInline
from .links import LinksInline
from .metadata import ApplicationAreasInline, TopicsInline
from .permissions import PermissionsInline
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


class JobFairCompaniesInline(admin.TabularInline):
    model = JobFairCompany
    extra = 0
    verbose_name = "company recruiter"
    # form
    raw_id_fields = ("institution", "users")


@admin.register(JobFair)
class JobFairAdmin(admin.ModelAdmin):
    date_hierarchy = "start_date"
    inlines = (InstitutionsInline, PermissionsInline, JobFairCompaniesInline)


@admin.register(JobFairRegistration)
class JobFairRegistrationAdmin(admin.ModelAdmin):
    actions = ("pdf_badges",)
    date_hierarchy = "created_at"
    list_display = (
        "id",
        "created_at",
        "name",
    )
    list_filter = ("fair",)
    search_fields = ("id", "user__email", "user__username", "user__first_name", "user__last_name")

    # custom actions

    @admin.action(description="ℹ️ Download badges")
    def pdf_badges(self, request, queryset):
        maker = JobFairBadgesPdfMaker(registrations=queryset, filename="badges.pdf")
        return maker.response

    # custom fields

    def name(self, obj):
        institution = obj.user.profile.institution.short_name if obj.user.profile.institution else "-"
        url = reverse("admin:auth_user_changelist")
        return format_html(
            f'<a href="{url}{obj.user_id}/" target="admin_user" class="text-nowrap">{obj.user.profile.name}</a>'
            f", {institution}"
        )
