HiPEAC.net
==========

[![travis-badge]][travis]
[![codecov-badge]][codecov]
[![codefactor-badge]][codefactor]
[![license-badge]](LICENSE)

The HiPEAC api/website uses [Django][django] and the [Django REST Framework][drf].

Application dependencies
------------------------

The application uses [Pipenv][pipenv] to manage Python packages. While in development, you will need to install
all dependencies (includes packages like `debug_toolbar`):

    $ pipenv install --dev
    $ pipenv shell

Update dependencies (and manually update `requirements.txt`):

    $ pipenv update --dev && pipenv lock -r

Running the server
------------------

    $ python manage.py migrate 
    $ python manage.py runserver

Running tests
-------------

    $ pytest --cov=hipeac --cov-report=term

Run Celery
----------

    $ celery worker -B -A hipeac

Style guide
-----------

Tab size is 4 spaces. Max line length is 120. You should run `flake8` and `black` before committing any change.

    $ flake8 hipeac
    $ black hipeac


[travis]: https://travis-ci.com/hipeac/hipeac?branch=master
[travis-badge]: https://api.travis-ci.com/hipeac/hipeac.svg?branch=master
[codecov]: https://codecov.io/gh/hipeac/hipeac
[codecov-badge]: https://codecov.io/gh/hipeac/hipeac/branch/master/graph/badge.svg
[codefactor]: https://www.codefactor.io/repository/github/hipeac/hipeac
[codefactor-badge]: https://www.codefactor.io/repository/github/hipeac/hipeac/badge
[license-badge]: https://img.shields.io/badge/license-MIT-blue.svg

[django]: https://www.djangoproject.com/
[drf]: https://www.django-rest-framework.org/
[pipenv]: https://docs.pipenv.org/#install-pipenv-today
