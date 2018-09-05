from django.views import generic

from hipeac.models import Article
from .mixins import SlugMixin


class ArticleDetail(SlugMixin, generic.DetailView):
    """
    Displays an Article.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """
    model = Article
    template_name = 'communication/article.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('images', 'institutions', 'projects')
