from django_countries import Countries

from hipeac.functions import get_european_countries, get_h2020_associated_countries


class HipeacCountries(Countries):
    only = get_european_countries() + get_h2020_associated_countries()
