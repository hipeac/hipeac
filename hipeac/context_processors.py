import os


def git_rev(request):
    return {
        'GIT_REV': os.environ.get('GIT_REV', None)
    }
