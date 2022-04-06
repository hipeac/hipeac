from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from hipeac.models.impact import TechTransferApplication, TechTransferAward, TechTransferCall
from .users import TeamMemberInline


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
