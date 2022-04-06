from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone

from hipeac.models.mixins import FilesMixin, ImagesMixin, InstitutionsMixin, ProjectsMixin


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_ready=True, publication_date__lte=timezone.now().date())


class Article(FilesMixin, ImagesMixin, InstitutionsMixin, ProjectsMixin, models.Model):
    TYPE_BLOG = "blog"
    TYPE_NEWS = "news"
    TYPE_RELEASE = "release"
    TYPE_JOBS = "jobs"
    TYPE_CHOICES = (
        (TYPE_BLOG, "HiPEAC Blog"),
        (TYPE_NEWS, "HiPEAC News"),
        (TYPE_RELEASE, "HiPEAC Press Release"),
        (TYPE_JOBS, "HiPEAC Career News"),
    )

    is_ready = models.BooleanField(default=False)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default=TYPE_NEWS)
    publication_date = models.DateField()
    title = models.CharField(max_length=250)
    excerpt = models.TextField()
    content = models.TextField()

    event = models.ForeignKey("hipeac.Event", null=True, blank=True, on_delete=models.SET_NULL, related_name="articles")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(), null=True, blank=True, on_delete=models.SET_NULL, related_name="authored_articles"
    )

    objects = ArticleQuerySet.as_manager()

    class Meta:
        db_table = "hipeac_comm_article"
        ordering = ("-publication_date",)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("article", args=[self.id, self.slug])

    def get_parent_url(self) -> str:
        return {
            self.TYPE_BLOG: f"{reverse('news')}#/blog/",
            self.TYPE_NEWS: reverse("news"),
            self.TYPE_RELEASE: reverse("press"),
            self.TYPE_JOBS: f"{reverse('jobs')}#/career-center/",
        }[self.type]

    def is_published(self) -> bool:
        return self.is_ready and self.publication_date <= timezone.now().date()

    @property
    def slug(self) -> str:
        return slugify(self.title)
