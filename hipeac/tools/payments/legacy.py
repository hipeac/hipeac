import os
import time
import unicodedata

from django.conf import settings
from django.contrib.sites.models import Site
from hashlib import sha512


OGONE_PSPID = os.environ.get("OGONE_PSPID_CONFERENCE")
OGONE_SALT = os.environ.get("OGONE_SALT")
OGONE_URL = os.environ.get("OGONE_URL")


def get_absolute_uri():
    protocol = "https://" if settings.SESSION_COOKIE_SECURE else "http://"
    return protocol + Site.objects.get_current().domain


def process_ogone_parameters(parameters, user):
    """
    This method checks if a minimum of parameters have been received,
    and then processes them: reorder parameters and include a SHA512 key built with all
    parameters. It adds also some common parameters, like language or currency.
    """
    # Common parameters
    logo = "https://gallery.mailchimp.com/3d4635dfec992c8c47c666ef5/images/51c538e3-2c1b-4a15-a6a3-6922e622fd85.png"
    ogone_parameters = {
        "CURRENCY": "EUR",
        "LANGUAGE": "en_US",
        "BGCOLOR": "#f5f5f5",
        "TXTCOLOR": "#222",
        "LOGO": logo,
    }
    # User parameters
    ogone_parameters.update(
        {
            "EMAIL": user.email,
            "CN": unicodedata.normalize("NFKD", user.profile.name).encode("ascii", "ignore").decode("utf-8").upper(),
        }
    )
    # Required parameters
    absolute_uri = get_absolute_uri()
    ogone_parameters.update(
        {
            "PSPID": parameters["PSPID"],
            "ORDERID": str(parameters["ORDERID"]) + "/" + str(int(time.time())),
            "AMOUNT": (parameters["AMOUNT"] * 100),
            "COM": "ID" + str(parameters["ORDERID"]),
            "ACCEPTURL": absolute_uri + parameters["RESULTURL"],
            "DECLINEURL": absolute_uri + parameters["RESULTURL"],
        }
    )
    # Generate SHA1 with sorted parameters
    string_to_hash = ""
    for key in sorted(ogone_parameters):
        string_to_hash += key + "=" + str(ogone_parameters[key]) + OGONE_SALT

    ogone_parameters.update({"SHASIGN": sha512(string_to_hash.encode("utf-8")).hexdigest().upper()})
    return ogone_parameters


class Ogone(object):
    SUCCESS_STATUSES = ("5", "51", "9", "91")
    EXCEPTION_STATUSES = ("52", "92")
    DECLINE_STATUSES = "2"
    CANCEL_STATUSES = "1"
    INVALID_STATUSES = "0"
