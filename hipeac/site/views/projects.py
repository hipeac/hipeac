from django.views import generic

from hipeac.models import Project
from .mixins import SlugMixin


class ProjectDetail(SlugMixin, generic.DetailView):
    """
    Displays a Project.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """
    model = Project
    template_name = 'network/project/project.html'

    def get_queryset(self):
        return super().get_queryset() \
                      .select_related('coordinator', 'coordinating_institution') \
                      .prefetch_related('partners', 'links')
