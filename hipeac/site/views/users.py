from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic

from hipeac.models import Profile


class UserProfile(generic.DetailView):
    """
    Displays a User profile.
    """
    model = Profile
    context_object_name = 'profile'
    slug_field = 'user__username'
    template_name = 'users/profile.html'

    def get_queryset(self):
        return super().get_queryset()


class UserSettings(generic.TemplateView):
    template_name = 'users/user/settings.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
