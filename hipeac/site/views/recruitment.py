from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.views import generic
from markdown import markdown as marked
from wkhtmltopdf.views import PDFTemplateResponse

from hipeac.models import Job
from .mixins import SlugMixin


class JobDetail(SlugMixin, generic.DetailView):
    """
    Displays a Job.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """
    model = Job
    template_name = 'recruitment/job.html'

    def get_queryset(self):
        return super().get_queryset().select_related('institution').prefetch_related('links')


class JobsFeed(Feed):
    title = 'HiPEAC Jobs'
    link = reverse_lazy('jobs')

    def items(self):
        return Job.objects.active().select_related('institution').order_by('-created_at')

    def item_title(self, item):
        return '{0} @ {1}'.format(item.title, item.institution)

    def item_description(self, item):
        return marked(item.description)


class JobsPdf(generic.DetailView):
    model = Job

    def get(self, request, *args, **kwargs):
        job = self.get_object()
        return PDFTemplateResponse(
            request=request,
            template='recruitment/jobs.pdf.html',
            filename='hipeac-jobs--%s.pdf' % job.id,
            context={
                'jobs': [job],
            },
            show_content_in_browser=True
        )
