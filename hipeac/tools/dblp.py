import lxml.html
import requests

from requests.exceptions import RequestException
from lxml.cssselect import CSSSelector

from hipeac.models import PublicationConference, Publication, Profile, Link


def parse_element(element, year: int):
    data_el = element.cssselect('.data')[0]
    title_el = element.cssselect('.data span.title')[0]

    try:
        url_el = element.cssselect('.publ > ul > li:first-child .head a')[0]
        url = url_el.get('href')
    except Exception:
        url = None

    return {
        'year': year,
        'title': title_el.text_content()[:-1],
        'authors_string': data_el.text_content().split(':')[0],
        'dblp_key': element.get('id'),
        'url': url,
        'itemtype': element.get('itemtype').rsplit('/', 1)[-1],
    }


def process_conference_publications(conference: PublicationConference):
    publications = {}

    try:
        r = requests.get(conference.url)
    except RequestException as e:
        return str(e)

    # Build the DOM Tree.
    tree = lxml.html.fromstring(r.text)
    # Apply a CSS selector to the DOM tree
    # and traverse each element to get the necessary information.
    sel = CSSSelector('ul.publ-list > li')

    for element in sel(tree):
        publications[element.get('id')] = parse_element(element, conference.year)

    # populate database
    for key, publication in publications.items():
        try:
            entry = Publication.objects.get(dblp_key=publication['dblp_key'])
        except Publication.DoesNotExist:
            entry = Publication(**publication)
            entry.save()
        entry.conference = conference
        entry.save()

    return True


def process_user_publications(profile: Profile):
    url_dblp = profile.get_link(Link.DBLP)

    if not url_dblp:
        return None

    publications = {}
    year = None
    # Request URL.
    try:
        r = requests.get(url_dblp)
    except RequestException as e:
        return str(e)

    # Build the DOM Tree.
    tree = lxml.html.fromstring(r.text)
    # Apply a CSS selector to the DOM tree
    # and traverse each element to get the necessary information.
    sel = CSSSelector('ul.publ-list > li')

    for element in sel(tree):
        if element.get('id') is None:
            year = int(element.text)
        else:
            publications[element.get('id')] = parse_element(element, year)

    # populate database
    for key, publication in publications.items():
        try:
            entry = Publication.objects.get(dblp_key=publication['dblp_key'])
        except Publication.DoesNotExist:
            entry = Publication(**publication)
            entry.save()
        entry.authors.add(profile)
        entry.save()

    return True
