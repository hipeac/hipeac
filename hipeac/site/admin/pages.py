from django.contrib import admin
from django.contrib.flatpages.models import FlatPage

from hipeac.models import Block
from .generic import HideDeleteActionMixin, ImagesInline


admin.site.unregister(FlatPage)


@admin.register(Block)
class BlockAdmin(HideDeleteActionMixin, admin.ModelAdmin):
    list_display = ('id', 'page', 'key')
    list_filter = ('page',)

    inlines = (ImagesInline,)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('key', 'notes')
        return ()
