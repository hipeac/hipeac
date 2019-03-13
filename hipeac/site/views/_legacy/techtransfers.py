from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic

from hipeac.models import TechTransferApplication


class TechTransferAwards(generic.ListView):
    model = TechTransferApplication
    template_name = '_legacy/techtransfers/awards.html'

    def get_queryset(self):
        return super().get_queryset().filter(status='OK') \
                                     .select_related('call') \
                                     .order_by('call__start_date', 'title')
