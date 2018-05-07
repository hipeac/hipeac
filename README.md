HiPEAC.net
==========

[![ci-badge]][ci]
[![coverage-badge]][coverage]
[![license-badge]](LICENSE)

The HiPEAC api/website uses [Django](https://www.djangoproject.com/) and the
[Django REST Framework](http://www.django-rest-framework.org/).

Application dependencies
------------------------
The application uses [Pipenv](https://docs.pipenv.org/#install-pipenv-today) to manage Python packages.
While in development, you will need to install all dependencies (includes packages like `debug_toolbar`):

    $ pipenv install --dev
    $ pipenv shell

Running the server
------------------
    $ python manage.py runserver

Running tests
-------------
    $ python manage.py test hipeac
    
Coverage of the tests
---------------------
    $ coverage run --source='hipeac' manage.py test hipeac
    $ coverage report -m

Run Celery
----------
    $ celery worker -B -A hipeac

Style guide
-----------
Unless otherwise specified, follow
[Django Coding Style](https://docs.djangoproject.com/en/1.11/internals/contributing/writing-code/coding-style/).
Tab size is 4 **spaces**. Maximum line length is 120. All changes should include tests and pass `flake8`.


[ci-badge]: https://travis-ci.org/hipeac/website.svg?branch=master
[ci]: https://travis-ci.org/hipeac/website?branch=master
[coverage-badge]: https://coveralls.io/repos/github/hipeac/website/badge.svg?branch=master
[coverage]: https://coveralls.io/r/hipeac/website?branch=master
[license-badge]: https://img.shields.io/badge/license-MIT-blue.svg
