from django.contrib import admin

from hipeac.models.events import SessionProposal


@admin.register(SessionProposal)
class SessionProposalAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user")
    list_filter = (("event", admin.RelatedOnlyFieldListFilter),)

    def user(self, obj):
        return f"{obj.first_name} {obj.last_name} <{obj.email}>"
