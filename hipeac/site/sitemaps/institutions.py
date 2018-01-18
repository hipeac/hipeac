from django.contrib.sitemaps import Sitemap

from hipeac.models import Institution


class InstitutionSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return Institution.objects.only('id', 'name', 'updated_at')

    def lastmod(self, obj):
        return obj.updated_at
