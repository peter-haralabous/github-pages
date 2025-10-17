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

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a
  "Verify Your E-mail Address" page. Go to [mailpit](http://localhost:8025) to see the emailed message. Follow the verification link and
  the user will be ready to go.

- To create a **superuser account**, use this command:

      uv run python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar),
so that you can see how the site behaves for both kinds of users.

## Essential Commands

**`make dev`** - Start development environment
Sets up everything you need and launches the dev server with hot reload.

**`make test`** - Run all tests
Executes both unit tests and end-to-end tests to verify your code works.

**`make test-unit`** - Run unit tests only
Quick feedback loop for testing your Python code changes.

**`make test-e2e`** - Run end-to-end tests
Full browser testing to ensure the complete application works correctly.

## Setup & Maintenance

**`make init`** - Initialize project
Sets up Python virtual environment, installs dependencies, and configures git hooks.

**`make lint`** - Check code quality
Runs formatting and linting tools to keep your code clean and consistent.

**`make coverage`** - Generate test coverage report
Shows which parts of your code are tested and opens the report in your browser.

## Utilities

**`make migrate`** - Apply database migrations
Updates your database schema with any pending changes.

**`make collectstatic`** - Prepare static files
Gathers CSS, JS, and other static assets for deployment.

### Testing Docker builds

```
docker compose up --build sandwich
```

## Testing outputs of an LLM

To run tests that use a real LLM (and record/replay HTTP interactions with VCR):

```sh
pytest --record-mode=all sandwich/core/services/ingest/extract_text_test.py
```

- The first run will record cassettes for all LLM calls.
- Subsequent runs will replay the recorded responses for fast, deterministic tests **without hitting the LLM again**.
- This avoids unnecessary API costs, rate limits, and unpredictable outputs from the LLM.
- To re-record, delete the cassette files or use `--record-mode=all` again.

See `extract_text_test.py` for example test cases and assertions.
