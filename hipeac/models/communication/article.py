from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone

from ..mixins import UrlMixin


class ArticleManager(models.Manager):
    def published(self):
        return self.filter(
            is_ready=True,
            publication_date__lte=timezone.now().date()
        )


class Article(UrlMixin, models.Model):
    route_name = 'article'

    TYPE_BLOG = 'blog'
    TYPE_NEWS = 'news'
    TYPE_RELEASE = 'release'
    TYPE_JOBS = 'jobs'
    TYPE_CHOICES = (
        (TYPE_BLOG, 'HiPEAC Blog'),
        (TYPE_NEWS, 'HiPEAC News'),
        (TYPE_RELEASE, 'HiPEAC Press Release'),
        (TYPE_JOBS, 'HiPEAC Career News'),
    )

    is_ready = models.BooleanField(default=False)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default=TYPE_NEWS)
    publication_date = models.DateField()
    title = models.CharField(max_length=250)
    excerpt = models.TextField()
    content = models.TextField()

    images = GenericRelation('hipeac.Image')
    projects = models.ManyToManyField('hipeac.Project', blank=True, related_name='articles')
    institutions = models.ManyToManyField('hipeac.Institution', blank=True, related_name='articles')

    created_at = models.DateTimeField()  # TODO: auto_now_add=True
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='authored_articles')

    objects = ArticleManager()

    class Meta(object):
        ordering = ['-publication_date']

    def __str__(self) -> str:
        return self.title

    """
    def get_parent_section(self):
        return {
            self.TYPE_BLOG: 'blog',
            self.TYPE_NEWS: 'news',
            self.TYPE_RELEASE: 'releases',
        }[self.type]

    def get_parent_url(self):
        return reverse('press:articles', args=[self.get_parent_section()])
    """

    def is_published(self):
        return self.is_ready and self.publication_date <= timezone.now().date()

    @property
    def slug(self) -> str:
        return slugify(self.title)
