from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

from hipeac.apps.core.functions import massage_tweet, clean_markdown, get_asset_path
from hipeac.apps.core.models import AbstractAsset, User, Institution, Project
from hipeac.apps.core.models import WideCharField


class ArticleManager(models.Manager):
    def published(self):
        return self.filter(
            status='OK',
            release_date__lte=timezone.now().date()
        )


class Article(models.Model):
    """
    HiPEAC articles and news.
    """
    STATUS_CHOICES = (
        ('NO', 'Draft'),
        ('OK', 'Published'),
    )
    TYPE_BLOG = 'BLOG'
    TYPE_NEWS = 'NEWS'
    TYPE_RELEASE = 'RELEASE'
    TYPE_JOBS = 'JOBS'
    TYPE_PROJECT = 'PROJECT'
    TYPE_CHOICES = (
        (TYPE_BLOG, 'HiPEAC blog'),
        (TYPE_NEWS, 'HiPEAC news'),
        (TYPE_RELEASE, 'HiPEAC press release'),
        (TYPE_JOBS, 'Career news'),
        (TYPE_PROJECT, 'Project news'),
    )

    release_date = models.DateField()
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default=TYPE_NEWS)
    project = models.ForeignKey(Project, related_name='articles', null=True, blank=True,
                                help_text='Only necessary for "Project news".')
    institutions = models.ManyToManyField(Institution, blank=True, related_name='articles',
                                          help_text='Optionally, indicate institutions mentioned in the article.')
    author = models.ForeignKey(User, related_name='authored_articles', default=1)
    title = WideCharField(max_length=250)
    slug = models.SlugField(max_length=250, editable=False)
    excerpt = models.TextField()
    body = models.TextField()
    url = models.URLField('More info', null=True, blank=True,
                          help_text='Add the source URL if this is not a HiPEAC generated content.')
    url_banner = models.URLField('Banner URL', null=True, blank=True,
                                 help_text='Use a banner from the hipeac.net website.')
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='NO')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ArticleManager()

    class Meta(object):
        ordering = ['-release_date']

    def clean(self):
        """
        Validates the model before saving.
        """
        if self.type == self.TYPE_PROJECT and self.project is None:
            raise ValidationError('You need to choose a project for "Project news".')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.title

    def get_absolute_url(self):
        return reverse('press:article', args=[str(self.id), self.slug])

    def get_parent_section(self):
        return {
            self.TYPE_BLOG: 'blog',
            self.TYPE_NEWS: 'news',
            self.TYPE_RELEASE: 'releases',
            self.TYPE_PROJECT: 'news'
        }[self.type]

    def get_parent_url(self):
        return reverse('press:articles', args=[self.get_parent_section()])

    def is_published(self):
        return self.status == 'OK' and self.release_date <= timezone.now().date()
    is_published.boolean = True

    def clean_excerpt(self):
        return clean_markdown(self.excerpt)

    def get_tweet_for_share_widget(self):
        return massage_tweet(self.title, True, True)
