from django.contrib.syndication.views import Feed
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from markdown import markdown as marked
from typing import List
from wkhtmltopdf.views import PDFTemplateResponse

from hipeac.models import Job
from .mixins import SlugMixin


class JobRedirect(generic.View):
    """
    Redirects short URLs to job page.
    This short URLs have the "hipeac.net/j7127" structure
    """
    def get(self, request, *args, **kwargs):
        job = get_object_or_404(Job, pk=kwargs.get('pk'))
        return redirect(job.get_absolute_url())


class JobDetail(SlugMixin, generic.DetailView):
    """
    Displays a Job.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """
    model = Job
    template_name = 'recruitment/job/job.html'

    def get_queryset(self):
        return super().get_queryset().select_related('institution').prefetch_related('links')


class JobsFeed(Feed):
    title = 'HiPEAC Jobs'
    link = reverse_lazy('jobs')

    def items(self):
        return Job.objects.active().select_related('institution').order_by('-created_at')

    def item_categories(self, item) -> List[str]:
        return [topic.value for topic in item.get_metadata('topics')]

    def item_title(self, item) -> str:
        return f'{item.title} @ {item.institution}'

    def item_description(self, item)-> str:
        return marked(item.description)

    def item_pubdate(self, item):
        return item.created_at

    def item_updateddate(self, item):
        return item.updated_at


class JobsPdf(generic.DetailView):
    model = Job

    def get(self, request, *args, **kwargs):
        job = self.get_object()
        return PDFTemplateResponse(
            request=request,
            template='recruitment/job/jobs.pdf.html',
            filename='hipeac-jobs--%s.pdf' % job.id,
            context={
                'jobs': [job],
            },
            show_content_in_browser=True
        )
