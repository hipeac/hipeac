# HiPEAC.net

[![github-tests-badge]][github-tests]
[![codecov-badge]][codecov]
[![codefactor-badge]][codefactor]
[![license-badge]](LICENSE)


## Backend

The HiPEAC api/website uses [Django][django] and the [Django REST Framework][drf].

### Application dependencies

The application uses [Poetry][poetry] to manage application dependencies.

```bash
poetry lock
poetry install --no-root
```

### Run the app in development mode

```bash
python manage.py runserver
```

### Run Celery worker

```bash
celery worker -B -A hipeac
```

### Run the tests

```bash
pytest --cov=hipeac --cov-report=term
```

### Style guide

Tab size is 4 spaces. Max line length is 120. You should run `ruff` before committing any change.

```bash
ruff format . && ruff check metis
```

## Frontend

Some parts of the website are developed as one page applications with [Vue][vue] (`vue` folder).
When working on these, it is necessary to start a node server in parallel, so Django can access the
modules via [Inertia][inertia].

```bash
yarn
yarn dev
```


[codecov]: https://codecov.io/gh/hipeac/hipeac
[codecov-badge]: https://codecov.io/gh/hipeac/hipeac/branch/master/graph/badge.svg
[codefactor]: https://www.codefactor.io/repository/github/hipeac/hipeac
[codefactor-badge]: https://www.codefactor.io/repository/github/hipeac/hipeac/badge
[github-tests]: https://github.com/hipeac/hipeac/actions?query=workflow%3A%22tests%22
[github-tests-badge]: https://github.com/hipeac/hipeac/workflows/tests/badge.svg
[license-badge]: https://img.shields.io/badge/license-MIT-blue.svg

[django]: https://www.djangoproject.com/
[drf]: https://www.django-rest-framework.org/
[inertia]: https://inertiajs.com/
[poetry]: https://python-poetry.org/
[vue]: https://vuejs.org/
