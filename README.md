# HiPEAC.net

[![github-actions-badge]][github-actions]
[![codecov-badge]][codecov]
[![codefactor-badge]][codefactor]
[![license-badge]](LICENSE)


The HiPEAC api/website uses [Django][django] and the [Django REST Framework][drf].

### Application dependencies

The application uses [Pipenv][pipenv] to manage Python packages. While in development, you will need to install
all dependencies (includes packages like `debug_toolbar`):

```bash
pipenv install --dev
pipenv shell
```

Update dependencies (and manually update `requirements.txt`):

```bash
pipenv update --dev && pipenv lock && pipenv requirements
```

### Running the server

```bash
python manage.py migrate 
python manage.py runserver
```

### Running tests

```bash
pytest --cov=hipeac --cov-report=term
```

### Run Celery

```bash
celery worker -B -A hipeac
```

### Style guide

Tab size is 4 spaces. Max line length is 120. You should run `black` before committing any change.

```bash
black hipeac
```


[codecov]: https://codecov.io/gh/hipeac/hipeac
[codecov-badge]: https://codecov.io/gh/hipeac/hipeac/branch/master/graph/badge.svg
[codefactor]: https://www.codefactor.io/repository/github/hipeac/hipeac
[codefactor-badge]: https://www.codefactor.io/repository/github/hipeac/hipeac/badge
[github-actions]: https://github.com/hipeac/hipeac/actions?query=workflow%3A%22tests%22
[github-actions-badge]: https://github.com/hipeac/hipeac/workflows/tests/badge.svg
[license-badge]: https://img.shields.io/badge/license-MIT-blue.svg

[django]: https://www.djangoproject.com/
[drf]: https://www.django-rest-framework.org/
[pipenv]: https://docs.pipenv.org/#install-pipenv-today
