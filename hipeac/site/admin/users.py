from django.contrib import admin

from hipeac.models import Profile
from .generic import HideDeleteActionMixin


@admin.register(Profile)
class ProfileAdmin(HideDeleteActionMixin, admin.ModelAdmin):
    list_display = ('user_id', 'username', 'name', 'membership_tags')

    raw_id_fields = ('user',)
    readonly_fields = ('user',)
