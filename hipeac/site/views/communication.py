import datetime

from commonmark import commonmark as marked
from django.contrib.syndication.views import Feed
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from typing import List

from hipeac.models import Article
from .mixins import SlugMixin


class ArticleRedirect(generic.View):
    """
    Redirects old URLs to article page.
    """

    def get(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs.get("pk"))
        return redirect(article.get_absolute_url())


class ArticleDetail(SlugMixin, generic.DetailView):
    """
    Displays an Article.
    If the slug doesn't match we make a 301 Permanent Redirect.
    """

    model = Article
    template_name = "communication/article/article.html"

    def get_queryset(self):
        return (
            super().get_queryset().prefetch_related("images", "rel_institutions__institution", "rel_projects__project")
        )


class NewsFeed(Feed):
    title = "HiPEAC News"
    link = reverse_lazy("news")

    def items(self):
        return Article.objects.published().order_by("-publication_date")[:30]

    def item_categories(self, item) -> List[str]:
        return [item.get_type_display()]

    def item_title(self, item) -> str:
        return item.title

    def item_description(self, item) -> str:
        return f"{marked(item.excerpt)}{marked(item.content)}"

    def item_pubdate(self, item):
        return datetime.datetime.combine(item.publication_date, datetime.time.min)
