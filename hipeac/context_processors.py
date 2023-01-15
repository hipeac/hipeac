import os


def app(request):
    return {
        "CONTACT_EMAIL": "info@hipeac.net",
    }


def sentry(request):
    return {
        "GIT_REV": os.environ.get("GIT_REV", None),
    }
