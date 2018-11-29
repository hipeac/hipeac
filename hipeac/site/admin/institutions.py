from django.contrib import admin
from django.forms import ModelForm

from hipeac.forms import ApplicationAreasChoiceField, TopicsChoiceField
from hipeac.models import Institution
from .generic import HideDeleteActionMixin, LinksInline, PermissionsInline


class InstitutionAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField()
    topics = TopicsChoiceField()


@admin.register(Institution)
class InstitutionAdmin(HideDeleteActionMixin, admin.ModelAdmin):
    form = InstitutionAdminForm
    exclude = ['updated_at']

    list_display = ('id', 'name', 'type', 'country')
    list_filter = ('type',)
    search_fields = ['name', 'local_name', 'colloquial_name']

    raw_id_fields = ['parent']
    inlines = [LinksInline, PermissionsInline]
    fieldsets = (
        (None, {
            'fields': ('type', 'name', 'local_name', 'colloquial_name'),
        }),
        ('INFO', {
            'fields': (('country', 'location'), 'description', 'image'),
        }),
        ('RECRUITMENT', {
            'fields': ('recruitment_contact', 'recruitment_email'),
        }),
        ('METADATA', {
            'classes': ('collapse',),
            'fields': ('application_areas', 'topics'),
        }),
    )
