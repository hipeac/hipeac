import hashlib
import re
import time
import unicodedata

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django_countries import Countries
from markdown import markdown


def get_absolute_uri():
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


class HipeacCountries(Countries):
    only = get_european_countries() + get_h2020_associated_countries()


"""
vvvvvvvvvvvvvvvvvvv
CHECK OLD FUNCTIONS
vvvvvvvvvvvvvvvvvvv
"""


def truncate(string):
    return string


def asset_post_delete_handler(sender, **kwargs):
    asset = kwargs['instance']
    storage, path = asset.file.storage, asset.file.path
    storage.delete(path)


def clean_markdown(text, truncate_length=False):
    text = truncate(text, truncate_length) if truncate_length else text
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', markdown(text))


def massage_tweet(tweet, link=False, via=False):
    limit = 140
    link_length = 24  # This is a default t.co link length
    text = re.sub(' +', ' ', tweet)

    if link:
        """
        if isinstance(link, basestring):
            ll = len(link)
            link_length = link_length if ll > link_length else ll
        """
        limit = limit - link_length - 1

    if via:
        limit = limit - 12

    text = truncate(text, limit).rstrip()
    return (text + ' ' + link) if isinstance(link, basestring) else text


def process_ogone_parameters(parameters, user):
    """
    This method checks if a minimum of parameters have been received,
    and then processes them: reorder parameters and include a SHA512 key built with all
    parameters. It adds also some common parameters, like language or currency.
    """
    # Common parameters
    logo = 'https://gallery.mailchimp.com/3d4635dfec992c8c47c666ef5/images/51c538e3-2c1b-4a15-a6a3-6922e622fd85.png'
    ogone_parameters = {
        'CURRENCY': 'EUR',
        'LANGUAGE': 'en_US',
        'BGCOLOR': '#f5f5f5',
        'TXTCOLOR': '#222',
        'LOGO': logo,
    }
    # User parameters
    ogone_parameters.update({
        'EMAIL': user.email,
        'CN': unicodedata.normalize('NFKD', user.full_name()).encode('ascii', 'ignore').upper(),
    })
    # Required parameters
    absolute_uri = get_absolute_uri()
    ogone_parameters.update({
        'PSPID': parameters['PSPID'],
        'ORDERID': str(parameters['ORDERID']) + '/' + str(int(time.time())),
        'AMOUNT': (parameters['AMOUNT'] * 100),
        'COM': 'ID' + str(parameters['ORDERID']),
        'ACCEPTURL': absolute_uri + parameters['RESULTURL'],
        'DECLINEURL': absolute_uri + parameters['RESULTURL'],
    })
    # Generate SHA1 with sorted parameters
    string_to_hash = ''
    for key in sorted(ogone_parameters):
        string_to_hash += key + '=' + str(ogone_parameters[key]) + settings.OGONE_SALT

    ogone_parameters.update({
        'SHASIGN': hashlib.sha512(string_to_hash).hexdigest().upper(),
    })
    return ogone_parameters


class Ogone(object):
    SUCCESS_STATUSES = ('5', '51', '9', '91')
    EXCEPTION_STATUSES = ('52', '92')
    DECLINE_STATUSES = ('2')
    CANCEL_STATUSES = ('1')
    INVALID_STATUSES = ('0')











def new_member_states():
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


def european_countries():
    """
    https://europa.eu/european-union/about-eu/countries_en < 2004
    """
    return new_member_states() + (
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


def h2020_associated_countries():
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
