The HiPEAC api/website uses [Django][1] and the [Django REST Framework][2].

### Application dependencies

The application uses [Pipenv][3] to manage Python packages. While in development, you will need to install
all dependencies (includes packages like `debug_toolbar`):

    $ pipenv install --dev
    $ pipenv shell

Update dependencies (and manually update `requirements.txt`):

    $ pipenv update --dev && pipenv lock -r

### Running the server

    $ python manage.py runserver

### Running tests

    $ pytest --cov=hipeac --cov-report=term

### Run Celery

    $ celery worker -B -A hipeac

### Style guide

Unless otherwise specified, follow [Django Coding Style][4]. Tab size is 4 **spaces**.
Maximum line length is 120. All changes should include tests and pass `flake8`.


[1]: https://www.djangoproject.com/
[2]: https://www.django-rest-framework.org/
[3]: https://docs.pipenv.org/#install-pipenv-today
[4]: https://docs.djangoproject.com/en/1.11/internals/contributing/writing-code/coding-style/
