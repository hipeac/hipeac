import lxml.html
import requests

from celery.decorators import periodic_task, task
from celery.schedules import crontab
from requests.exceptions import RequestException
from lxml.cssselect import CSSSelector

from hipeac.models import PublicationConference, Publication, Profile, Link


@task(rate_limit='60/m')
def extract_publications_for_conference(conference_id):
    event = PublicationConference.objects.get(id=conference_id)
    publications = {}

    try:
        r = requests.get(event.url)
    except RequestException as e:
        return str(e)

    # Build the DOM Tree.
    tree = lxml.html.fromstring(r.text)
    # Apply a CSS selector to the DOM tree
    # and traverse each element to get the necessary information.
    sel = CSSSelector('ul.publ-list > li')

    for element in sel(tree):
        data_el = element.cssselect('div.data')[0]
        title_el = element.cssselect('div.data span.title')[0]
        try:
            url_el = element.cssselect('.publ > ul > li:first-child .head a')[0]
            url = url_el.get('href')
        except Exception:
            url = None

        publications[element.get('id')] = {
            'year': event.year,
            'title': title_el.text_content()[:-1],
            'authors_string': data_el.text_content().split(':')[0],
            'dblp_key': element.get('id'),
            'url': url,
            'itemtype': element.get('itemtype').rsplit('/', 1)[-1],
        }

    # populate database
    for key, publication in publications.items():
        try:
            entry = Publication.objects.get(dblp_key=publication['dblp_key'])
        except Publication.DoesNotExist:
            entry = Publication(**publication)
            entry.save()
        entry.conference = event
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
            year = element.text
        else:
            data_el = element.cssselect('div.data')[0]
            title_el = element.cssselect('div.data span.title')[0]

            try:
                url_el = element.cssselect('.publ > ul > li:first-child .head a')[0]
                url = url_el.get('href')
            except Exception:
                url = None

            publications[element.get('id')] = {
                'year': int(year),
                'title': title_el.text_content()[:-1],
                'authors_string': data_el.text_content().split(':')[0],
                'dblp_key': element.get('id'),
                'url': url,
                'itemtype': element.get('itemtype').rsplit('/', 1)[-1],
            }

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


@task(rate_limit='60/m')
def extract_publications_for_user(user_id):
    profile = Profile.objects.prefetch_related('links').get(user_id=user_id)
    process_user_publications(profile)


@periodic_task(run_every=crontab(day_of_week='sun', hour=3, minute=0))
def check_member_publications():
    for profile in Profile.objects.exclude(membership_tags__is_null=True) \
                                  .exclude(membership_tags__exact='') \
                                  .filter(profile__membership_revocation_date__isnull=True):
        process_user_publications(profile)
