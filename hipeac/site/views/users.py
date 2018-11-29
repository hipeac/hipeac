from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic


class UserProfile(generic.DetailView):
    """
    Displays a User profile.
    """
    model = get_user_model()
    context_object_name = 'the_user'
    slug_field = 'username'
    template_name = 'users/profile.html'

    def get_queryset(self):
        return super().get_queryset()


class UserSettings(generic.TemplateView):
    template_name = 'users/user/settings.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
