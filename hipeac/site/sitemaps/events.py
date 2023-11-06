from django.contrib.sitemaps import Sitemap

from hipeac.models import Event, Session


class EventSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return Event.objects.only("id", "city", "start_date", "end_date")

    def lastmod(self, obj):
        return obj.end_date


class SessionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return Session.objects.only("id", "title", "updated_at", "event")

    def lastmod(self, obj):
        return obj.updated_at
