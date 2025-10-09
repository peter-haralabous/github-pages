.PHONY: init
init: .venv node_modules
	[ -x .git/hooks/pre-commit ] || uv run pre-commit install

.venv: pyproject.toml uv.lock
	uv sync
	@touch $@

node_modules: package.json yarn.lock
	yarn install
	@touch $@

.playwright-browsers: pyproject.toml
	uv run playwright install --with-deps chromium
	@touch $@

.PHONY: collectstatic
collectstatic: .venv build-js
	uv run manage.py collectstatic --noinput

.PHONY: build-js
build-js: node_modules
	yarn run build

.PHONY: migrate
migrate: postgres
	uv run manage.py migrate

.PHONY: mailpit
mailpit:
	docker compose up -d mailpit

.PHONY: postgres
postgres:
	docker compose up -d postgres

.PHONY: dev
dev: init collectstatic migrate mailpit postgres
	yarn run dev

.PHONY: test-unit
test-unit: .venv postgres
	uv run pytest -m "not e2e and not smoke_test" --exitfirst # --snapshot-update

.PHONY: test-e2e
test-e2e: .playwright-browsers collectstatic
	# https://pytest-xdist.readthedocs.io/en/stable/distribution.html
	uv run pytest -m e2e --numprocesses logical --exitfirst

.PHONY: test
test: test-unit test-e2e

.PHONY: coverage
coverage:
	uv run coverage run -m pytest
	uv run coverage html
	open htmlcov/index.html

.PHONY: lint
lint: init
	uv run pre-commit run -a

.PHONY: smoke-test-development
smoke-test-development:
	uv run --script ./scripts/check_version.py \
		http://localhost:3000/ \
		"latest"

.PHONY: smoke-test-integration
smoke-test-integration: .playwright-browsers
	uv run --script ./scripts/check_version.py \
		https://hc.wethrive.ninja/ \
		"${GITHUB_SHA}"
	uv run pytest -m smoke_test --numprocesses logical --exitfirst

.PHONY: smoke-test-production
smoke-test-production:
	uv run --script ./scripts/check_version.py \
		https://hc.thrive.health/ \
		"${GITHUB_SHA}"

.PHONY: data
data:
	uv run manage.py data generate

.PHONY: save-fixtures
save-fixtures:
	uv run manage.py dumpdata --natural-primary --natural-foreign --indent 2 \
		core.organization > sandwich/core/fixtures/organization.json
	uv run manage.py dumpdata --natural-primary --natural-foreign --indent 2 \
		core.template > sandwich/core/fixtures/template.json
	uv run pre-commit run --all-files prettier || true

.PHONY: load-fixtures
load-fixtures:
	uv run manage.py loaddata organization template
