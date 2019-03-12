from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic

from hipeac.models import InternshipApplication


class InternshipAwardees(generic.ListView):
    model = InternshipApplication
    template_name = '_legacy/internships/awardees.html'

    def get_queryset(self):
        return super().get_queryset().filter(selected=True) \
                                     .select_related('internship__call') \
                                     .prefetch_related('internship__institution', 'created_by__profile__institution') \
                                     .order_by('internship__call__start_date', 'created_by__first_name')
