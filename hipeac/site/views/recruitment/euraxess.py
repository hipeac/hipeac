from django.views import generic

from hipeac.models import Job
from hipeac.models.countries import HipeacCountries
from hipeac.tools.euraxess import EuraxessXMLGenerator


valid_countries = {c.code for c in HipeacCountries()}


class JobsEuraxessXML(generic.View):
    queryset = (
        Job.objects.active()
        .filter(country__in=valid_countries, institution__country__in=valid_countries)
        .order_by("-created_at")
    )

    def get(self, request, *args, **kwargs):
        generator = EuraxessXMLGenerator(queryset=self.queryset)
        return generator.response
