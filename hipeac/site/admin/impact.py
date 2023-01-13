from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from hipeac.functions import send_task
from hipeac.models.impact import PublicationConference, TechTransferApplication, TechTransferAward, TechTransferCall
from hipeac.site.pdfs.awards import TechTransferCallPdfMaker
from .users import TeamMemberInline


@admin.register(PublicationConference)
class PublicationConferenceAdmin(admin.ModelAdmin):
    actions = ("extract_publications_from_dblp",)
    list_display = ("id", "name")
    list_filter = ("year",)

    def name(self, obj):
        return str(obj)

    def extract_publications_from_dblp(self, request, queryset):
        for conference in queryset:
            send_task("hipeac.tasks.dblp.extract_publications_for_conference", (conference.id,))
        admin.ModelAdmin.message_user(
            self, request, "Publication extraction has started, " "results from DBLP will be available soon."
        )
        return True

    extract_publications_from_dblp.short_description = "[DATA] Extract publications from DBLP"


class TechTransferAwardInline(admin.StackedInline):
    model = TechTransferAward
    classes = ("collapse",)
    extra = 0
    verbose_name = "award"
    # form
    raw_id_fields = ("awardee", "origin_institution", "recipient_institution")
    inlines = (TeamMemberInline,)


@admin.register(TechTransferApplication)
class TechTransferApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "call", "title", "awarded")
    list_filter = ("call",)
    search_fields = ("title",)
    # form
    raw_id_fields = ("call", "applicant")
    readonly_fields = ("call",)
    inlines = (TechTransferAwardInline,)

    def has_module_permission(self, request):
        return False

    # custom fields

    def awarded(self, obj) -> bool:
        return hasattr(obj, "award")

    awarded.boolean = True


@admin.register(TechTransferCall)
class TechTransferCallAdmin(admin.ModelAdmin):
    actions = ("export_pdf",)
    list_display = ("id", "start_date", "end_date", "applications_link")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(Count("applications", distinct=True))

    # custom fields

    def applications_link(self, obj):
        if obj.applications__count == 0:
            return "-"
        url = reverse("admin:hipeac_techtransferapplication_changelist")
        return format_html(f'<a href="{url}?call__id__exact={obj.id}">{obj.applications__count}</a>')

    applications_link.short_description = "Applications"

    # actions

    def pdf_response(self, calls, filename: str = "hipeac--calls.pdf", as_attachment: bool = False):
        maker = TechTransferCallPdfMaker(calls=calls, filename=filename, as_attachment=as_attachment)
        return maker.response

    def export_pdf(self, request, queryset):
        return self.pdf_response(queryset)

    export_pdf.short_description = "[PDF] Generate printable document for selected calls"
