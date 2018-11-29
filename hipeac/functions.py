from celery.execute import send_task as celery_send_task
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site


def get_absolute_uri() -> str:
    protocol = 'https://' if settings.SESSION_COOKIE_SECURE else 'http://'
    return protocol + Site.objects.get_current().domain


def get_images_path(instance, filename):
    content_type = ContentType.objects.get_for_model(instance)
    extension = filename.rsplit('.', 1)[1]
    return ''.join(['public/images/', str(content_type.id), '/', str(instance.id), '.', extension])


def get_european_countries():
    """
    https://europa.eu/european-union/about-eu/countries_en < 2004
    """
    return get_new_member_states() + (
        'AT',  # Austria (1995)
        'BE',  # Belgium (1958)
        'DK',  # Denmark (1973)
        'FI',  # Finland (1995)
        'FR',  # France (1958)
        'DE',  # Germany (1958)
        'GR',  # Greece (1981)
        'IE',  # Ireland (1973)
        'IT',  # Italy (1958)
        'LU',  # Luxembourg (1958)
        'NL',  # Netherlands (1958)
        'PT',  # Portugal (1986)
        'ES',  # Spain (1986)
        'SE',  # Sweden (1995)
        'GB',  # United Kingdom (1973)
    )


def get_new_member_states():
    """
    https://europa.eu/european-union/about-eu/countries_en >= 2004
    """
    return (
        'BG',  # Bulgaria (2007)
        'HR',  # Croatia (2013)
        'CY',  # Cyprus (2004)
        'CZ',  # Czech Republic (2004)
        'EE',  # Estonia (2004)
        'HU',  # Hungary (2004)
        'LV',  # Latvia (2004)
        'LT',  # Lithuania (2004)
        'MT',  # Malta (2004)
        'PL',  # Poland (2004)
        'RO',  # Romania (2007)
        'SK',  # Slovakia (2004)
        'SI',  # Slovenia (2004)
    )


def get_h2020_associated_countries():
    """
    http://ec.europa.eu/research/participants/data/ref/h2020/grants_manual/hi/3cpart/h2020-hi-list-ac_en.pdf
    """
    return (
        'AL',  # Albania
        'AM',  # Armenia
        'BA',  # Bosnia and Herzegovina
        'FO',  # Faroe Islands
        'GE',  # Georgia
        'IS',  # Iceland
        'IL',  # Israel
        'MK',  # Macedonia, the former Yugoslav Republic of
        'MD',  # Moldova
        'ME',  # Montenegro
        'NO',  # Norway
        'RS',  # Serbia
        'CH',  # Switzerland (partial association, see below)
        'TN',  # Tunisia
        'TR',  # Turkey
        'UA',  # Ukraine
    )


def send_task(*args, **kwargs):
    if not settings.TEST:
        celery_send_task(*args, **kwargs)
