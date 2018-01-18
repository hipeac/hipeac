from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from registration.backends.hmac import views as hmac_views
from registration.forms import RegistrationFormUniqueEmail


class ActivationView(hmac_views.ActivationView):
    template_name = 'registration/activate.html'


class ActivationCompleteView(TemplateView):
    template_name = 'registration/activation_complete.html'


class RegistrationView(hmac_views.RegistrationView):
    form_class = RegistrationFormUniqueEmail
    template_name = 'registration/registration_form.html'
    redirect_authenticated_user = True


class RegistrationCompleteView(TemplateView):
    template_name = 'registration/registration_complete.html'


class LoginView(auth_views.LoginView):
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    pass


class PasswordChangeView(auth_views.PasswordChangeView):
    pass


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    pass


class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'registration/password_reset_email.txt'


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    pass


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    pass


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    pass
