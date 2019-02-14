from commonmark import commonmark as marked
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic
from typing import List

from hipeac.models import Job, JobEvaluation
from hipeac.site.pdfs.recruitment import JobsPdfMaker
from .mixins import SlugMixin


class JobRedirect(generic.View):
    """
    Redirects short URLs to job page.
    This short URLs have the "hipeac.net/j7127" structure
    """
    def get(self, request, *args, **kwargs):
        job = get_object_or_404(Job, pk=kwargs.get('pk'))
        return redirect(job.get_absolute_url())


class JobManagementView(generic.ListView):
    """
    Displays a list of jobs posted by a user.
    """
    context_object_name = 'jobs'
    template_name = 'recruitment/management.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Job.objects.filter(created_by=self.request.user.id).prefetch_related('institution').order_by('-deadline')


class JobDetail(SlugMixin, generic.DetailView):
    """
    Displays a Job.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """
    model = Job
    template_name = 'recruitment/job/job.html'

    def get_queryset(self):
        return super().get_queryset().select_related('institution').prefetch_related('links')


class JobEvaluationRedirect(generic.View):
    """
    Creates a evaluation for a Job and redirects to the evaluation editor.
    """
    def get(self, request, *args, **kwargs):
        try:
            evaluation = JobEvaluation.objects.get(job_id=kwargs.get('job_id'))
            evaluation.value = kwargs.get('value')
        except JobEvaluation.DoesNotExist:
            evaluation = JobEvaluation(job_id=kwargs.get('job_id'), value=kwargs.get('value'))

        evaluation.save()
        return redirect(evaluation.get_editor_url())


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
        maker = JobsPdfMaker(jobs=[job], filename=f'hipeac-jobs--{job.id}.pdf', as_attachment=False)
        return maker.response
