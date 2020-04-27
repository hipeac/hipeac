from django.views import generic

from hipeac.models import Institution
from .mixins import SlugMixin


class InstitutionDetail(SlugMixin, generic.DetailView):
    """
    Displays a Institution.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """

    model = Institution
    template_name = "network/institution/institution.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("parent")
            .prefetch_related("children", "coordinated_projects", "links")
        )
