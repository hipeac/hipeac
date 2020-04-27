from django.contrib.sitemaps import Sitemap

from hipeac.models import Project


class ProjectSitemap(Sitemap):
    def items(self):
        return Project.objects.only("id", "acronym", "updated_at", "start_date", "end_date")

    def changefreq(self, obj):
        return "weekly" if obj.is_active() else "monthly"

    def lastmod(self, obj):
        return obj.updated_at

    def priority(self, obj):
        return 1.0 if obj.is_active() else 0.5
