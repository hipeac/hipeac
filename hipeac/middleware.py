from django.contrib.sites.shortcuts import get_current_site
from django.utils.deprecation import MiddlewareMixin


class CurrentSiteMiddleware(MiddlewareMixin):
    """
    Middleware that sets `site` attribute to request object.
    """

    def process_request(self, request):
        """Extend process_request to set `site` attribute, and choose correct urlconf."""
        request.site = get_current_site(request)
        request.urlconf = "hipeac.urls" if request.site.name == "HiPEAC" else "hipeac.urls_cc"
