from django.contrib.sitemaps import Sitemap

from hipeac.models import Job


class JobSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return Job.objects.active().only('id', 'title', 'updated_at')

    def lastmod(self, obj):
        return obj.updated_at
