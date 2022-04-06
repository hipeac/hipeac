import cloudscraper
import lxml.html
import re

from requests.exceptions import RequestException
from lxml.cssselect import CSSSelector

from hipeac.models.impact import TopScientist


def __parse_scientist_item(element, country_code: str) -> TopScientist:
    rankings = element.cssselect(".positions")[0].cssselect("span.position")
    info_el = element.cssselect(".info")[0]
    research = element.cssselect(".rankings-info")[0].cssselect("span.ranking > span.ranking")

    name_el = info_el.cssselect("h4 > a")[0]

    return TopScientist(
        ranking=int(re.findall(r"\d+", rankings[0].text)[0]),
        country=country_code,
        country_ranking=int(re.findall(r"\d+", rankings[1].text)[0]),
        name=name_el.text,
        affiliation=info_el.cssselect("span.sh")[0].text,
        h_index=int(re.findall(r"\d+", research[0].text)[0]),
        citations=int(re.findall(r"\d+", research[1].text.replace(",", ""))[0]),
        publications=int(re.findall(r"\d+", research[2].text)[0]),
        url=name_el.get("href"),
    )


def __process_country_rankings(country_code: str, page: int = 1):
    url = f"https://research.com/scientists-rankings/computer-science/{country_code}?page={page}"
    scraper = cloudscraper.create_scraper()
    bulk = []

    r = scraper.get(url)
    tree = lxml.html.fromstring(r.text)
    sel = CSSSelector("div.scientist-item")

    for item in sel(tree):
        bulk.append(__parse_scientist_item(item, country_code))

    TopScientist.objects.bulk_create(bulk, batch_size=1000)


def process_country_rankings(country_code: str):
    url = f"https://research.com/scientists-rankings/computer-science/{country_code}"
    scraper = cloudscraper.create_scraper()

    try:
        r = scraper.get(url)
        tree = lxml.html.fromstring(r.text)
        sel = CSSSelector("div.rankings-pagination > a")
        pages = len(sel(tree))

        if pages > 0:
            for page in range(1, pages + 1):
                __process_country_rankings(country_code, page)
        else:
            __process_country_rankings(country_code, 1)

    except RequestException as e:
        return str(e)

    return
