from commonmark import commonmark as marked
from django.contrib.syndication.views import Feed
from django.shortcuts import redirect, get_object_or_404
from django.template.defaultfilters import date as date_filter
from django.urls import reverse_lazy
from django.views import generic
from typing import List

from hipeac.models import Job, JobEvaluation

from hipeac.tools.pdf import PdfResponse, Pdf
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


class JobsPdfMaker:

    def __init__(self, *, jobs, filename: str, as_attachment: bool = False):
        self._response = PdfResponse(filename=filename, as_attachment=as_attachment)
        self.jobs = jobs
        self.make_pdf()

    def make_pdf(self):
        with Pdf() as pdf:
            for job in self.jobs:
                location = f'{job.location}, {job.country.name}' if job.location else job.country.name

                pdf.add_note(f'Find more on our web: hipeac.net/jobs/{job.id}')
                if job.institution:
                    pdf.add_text(f'<strong>{job.institution.name}</strong>', 'h4')
                pdf.add_text(location, 'h4')
                pdf.add_spacer()
                pdf.add_text(job.title, 'h1')
                pdf.add_text(f'<strong>Deadline</strong>: {date_filter(job.deadline)}', 'ul_li')
                pdf.add_text(f'<strong>Career levels</strong>: {job.get_metadata_display("career_levels")}', 'ul_li')
                pdf.add_text(f'<strong>Keywords</strong>: {job.get_metadata_display("topics")}', 'ul_li')
                pdf.add_text(job.description, 'markdown')
                pdf.add_page_break()

            self._response.write(pdf.get())

    @property
    def response(self) -> PdfResponse:
        return self._response
