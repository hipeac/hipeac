import os


def app(request):
    return {}


def sentry(request):
    return {
        'GIT_REV': os.environ.get('GIT_REV', None)
    }
