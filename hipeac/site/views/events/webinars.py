from django.views import generic


class WebinarList(generic.TemplateView):
    """Displays the general webinars page, not linked to an event."""

    template_name = "__v3__/events/webinars/webinars.html"
