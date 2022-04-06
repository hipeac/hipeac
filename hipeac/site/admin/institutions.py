from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from hipeac.models.institutions import Institution, RelatedInstitution
from .links import LinksInline
from .metadata import ApplicationAreasInline, TopicsInline
from .permissions import PermissionsInline


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "country")
    list_filter = ("type",)
    search_fields = ("name", "local_name", "colloquial_name", "country")
    # form
    raw_id_fields = ("parent",)
    inlines = (ApplicationAreasInline, TopicsInline, LinksInline, PermissionsInline)


class InstitutionsInline(GenericTabularInline):
    model = RelatedInstitution
    classes = ("collapse",)
    extra = 0
    verbose_name = "institution"
    # form
    raw_id_fields = ("institution",)


class PartnersInline(InstitutionsInline):
    verbose_name = "partner"


class SponsorsInline(InstitutionsInline):
    verbose_name = "sponsor"
