from django.contrib import admin

from hipeac.models.events import SessionProposal


@admin.register(SessionProposal)
class SessionProposalAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    list_filter = (("event", admin.RelatedOnlyFieldListFilter),)
