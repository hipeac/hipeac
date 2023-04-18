from django.views import generic


class VisionDetail(generic.TemplateView):
    """
    Displays Vision information.
    """

    template_name = "__v3__/vision/2023/index.html"
