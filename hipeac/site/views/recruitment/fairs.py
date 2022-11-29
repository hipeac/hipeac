from django.views import generic

from hipeac.models import JobFair


class JobFairView(generic.DetailView):
    """
    Shows the Job fair management page. a list of jobs posted by a user.
    """

    model = JobFair
    template_name = "__v3__/recruitment/fairs/fair.html"

    def get_object(self, queryset=None):
        if not hasattr(self, "object"):
            self.object = self.get_queryset().get(code=self.kwargs.get("code"))
        return self.object
