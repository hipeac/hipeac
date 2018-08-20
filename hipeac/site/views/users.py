from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic

from hipeac.models import Profile
from hipeac.site.forms import UserPrivacyForm, UserProfileForm


class UserSettings(generic.edit.UpdateView):
    model = Profile
    template_name = 'users/settings.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return Profile.objects.get(user=self.request.user)


class PrivacySettings(UserSettings):
    form_class = UserPrivacyForm

    def get_success_url(self):
        return reverse('user_privacy')


class ProfileSettings(UserSettings):
    form_class = UserProfileForm

    def get_success_url(self):
        return reverse('user_profile')
