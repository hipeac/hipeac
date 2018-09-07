from django.views import generic

from hipeac.models import Event, Roadshow
from .mixins import SlugMixin


class EventDetail(SlugMixin, generic.DetailView):
    """
    Displays a Event page.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """
    model = Event
    template_name = 'events/event/event.html'

    def get_queryset(self):
        return super().get_queryset().select_related('coordinating_institution')

    def get_object(self, queryset=None):
        if not hasattr(self, 'object'):
            if self.kwargs.get('pk', None):
                self.object = self.get_queryset().get(id=self.kwargs.get('pk'))
            else:
                self.object = self.get_queryset().get(
                    type=self.request.resolver_match.url_name,
                    start_date__year=self.kwargs.get('year'),
                    slug=self.kwargs.get('slug')
                )
        return self.object


class RoadshowDetail(SlugMixin, generic.DetailView):
    """
    Displays a Roadshow.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """
    model = Roadshow
    template_name = 'events/roadshow/roadshow.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('institutions')

    def get_object(self, queryset=None):
        if not hasattr(self, 'object'):
            self.object = self.get_queryset().get(id=self.kwargs.get('pk'))
        return self.object
