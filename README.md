# sandwich

bread + htmx

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)

## Quickstart

```shell
make dev
```

The application will be available at http://localhost:3000

All emails that the app sends will be viewable at http://localhost:8025

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to [mailpit](http://localhost:8025) to see the emailed message. Follow the verification link and the user will be ready to go.

- To create a **superuser account**, use this command:

      uv run python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    uv run mypy .

### Running tests

    uv run pytest

#### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    uv run coverage run -m pytest
    uv run coverage html
    open htmlcov/index.html

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

### Testing Docker builds

```shell
docker build -t sandwich .
docker run \
  -e DJANGO_SETTINGS_MODULE=config.settings.production \
  -e DJANGO_SECRET_KEY=secret \
  -e DJANGO_AWS_STORAGE_BUCKET_NAME=bucket-name \
  -e "DJANGO_ALLOWED_HOSTS=*" \
  -e DJANGO_SECURE_SSL_REDIRECT=false \
  -v ./data:/app/data \
  -p 3000:5000 \
  --rm sandwich
```
