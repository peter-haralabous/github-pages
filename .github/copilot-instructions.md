# Copilot Instructions for sandwich

This repository is a Django web application built with HTMX and Tailwind CSS for creating healthcare-related forms and workflows.

## Technology Stack

- **Backend**: Django 5.2.7 with Python 3.13
- **Frontend**: HTMX 2.0, Tailwind CSS 4, DaisyUI 5
- **Database**: PostgreSQL
- **Testing**: pytest with pytest-django for unit tests, Playwright for E2E tests
- **Package Management**:
  - Python: `uv` (not pip or poetry)
  - JavaScript: `yarn` (not npm)
- **Linting & Formatting**: Ruff (Python), Prettier (JS/CSS), djLint (Django templates), mypy (type checking), TypeScript

## Project Structure

- `sandwich/` - Main Django application code
  - `core/` - Core models and utilities
  - `patients/` - Patient-related functionality
  - `providers/` - Provider-related functionality
  - `users/` - User management
  - `templates/` - Django templates (HTMX-powered)
  - `static/` - Static assets
- `config/` - Django settings and configuration
- `webpack/` - Webpack configuration for frontend builds
- `docs/` - Project documentation

## Development Workflow

### Essential Commands

- **Start development**: `make dev` - Sets up and starts the dev server
- **Run tests**: `make test` (all), `make test-unit`, `make test-e2e`, `make test-frontend`
- **Lint code**: `make lint` - Runs all pre-commit hooks
- **Database migrations**: `make migrate`
- **Initialize project**: `make init` - Sets up venv, installs dependencies

### Code Style Guidelines

1. **Python**:
   - Use type hints for all functions and methods
   - Follow Django conventions for models, views, and URLs
   - Test files must end with `_test.py` (not `test_*.py`)
   - Use factory_boy factories for test data (see `factories.py` files)
   - Configure mypy with `django-stubs` for Django-specific type checking

2. **Templates**:
   - Use HTMX attributes for dynamic interactions
   - Follow Django template conventions
   - Use Tailwind CSS classes for styling (no custom CSS unless necessary)
   - Use DaisyUI components where applicable

3. **JavaScript/TypeScript**:
   - Write TypeScript when possible
   - Use Lit for web components
   - Keep JavaScript minimal - prefer HTMX for interactivity

4. **Testing**:
   - Unit tests: pytest with `pytest-django`
   - Frontend Unit tests: vitest
   - E2E tests: Playwright with pytest-playwright
   - Mark E2E tests with `@pytest.mark.e2e`
   - Use `--snapshot-update` for updating snapshots
   - Tests run against a test database with `--reuse-db`

### Important Conventions

- **Never use pip directly** - Always use `uv run` or ensure commands run through uv
- **Never use npm** - Always use `yarn` for JavaScript packages
- **Migrations**: Always check for pending migrations with pre-commit hooks
- **Pre-commit hooks**: Must pass before committing (run `make lint`)
- **Type checking**: Code must pass mypy type checking
- **URL naming**: Django URL patterns should have names for reverse lookups

### Common Patterns

1. **Views**: Prefer class-based views inheriting from Django's generic views
2. **Forms**: Use django-crispy-forms with crispy-tailwind for form rendering
3. **Permissions**: Use django-guardian for object-level permissions
4. **Background tasks**: Use procrastinate for async task processing
5. **API responses**: Return HTMX-compatible HTML fragments, not JSON (unless building a REST API)

### File Locations

- Add new Django apps under `sandwich/`
- Templates go in `sandwich/templates/` or app-specific template directories
- Static files (CSS, JS) source in `sandwich/static/` (compiled by webpack)
- Test factories in `<app>/factories.py`
- Test fixtures in `<app>/fixtures/` as JSON files

### Configuration

- Environment variables managed via `django-environ`
- Settings split by environment in `config/settings/`
- Use Datadog for monitoring and logging in production
- Content Security Policy configured via `django-csp`

## When Making Changes

1. Run `make init` if dependencies changed
2. Run `make migrate` if models changed
3. Run `make lint` before committing
4. Run `make test-unit` for quick feedback
5. Run `make test-frontend` for quick feedback
5. Run `make test-e2e` for full integration testing
6. Check that the dev server works with `make dev`

## Helpful Context

- This is a healthcare application, so be mindful of patient privacy and data security
- The application uses HTMX to provide SPA-like interactivity without complex JavaScript
- Tailwind CSS classes should be used for all styling
- The app uses email for notifications (mailpit in dev at localhost:8025)
