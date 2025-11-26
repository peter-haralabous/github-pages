import json
from pathlib import Path
from typing import TypedDict

from django.db import transaction

from sandwich.core.models import Form
from sandwich.core.models import Organization
from sandwich.core.models import SummaryTemplate


class FixtureConfig(TypedDict):
    name: str
    description: str
    form_data_file: str
    template_data_file: str


class FixtureResults(TypedDict):
    created_forms: int
    updated_forms: int
    created_templates: int
    updated_templates: int
    errors: list[str]


def _load_form_from_fixture(
    fixtures_dir: Path, fixture_config: FixtureConfig, organization: Organization
) -> tuple[Form | None, bool, str | None]:
    form_data_path = fixtures_dir / fixture_config["form_data_file"]
    if not form_data_path.exists():
        return None, False, f"Form data file not found: {form_data_path}"

    try:
        with form_data_path.open() as f:
            form_json = json.load(f)
            if isinstance(form_json, list) and len(form_json) > 0:
                form_fields = form_json[0]["fields"]
            else:
                return None, False, f"Invalid form data format in {fixture_config['form_data_file']}"

    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
        return None, False, f"Failed to load form from {fixture_config['form_data_file']}: {e}"

    form_name = form_fields["name"]
    existing_form = Form.objects.filter(organization=organization, name=form_name).first()

    if existing_form:
        existing_form.schema = form_fields["schema"]
        existing_form.status = form_fields.get("status", "active")
        existing_form.save()
        return existing_form, False, None

    new_form = Form.objects.create(
        organization=organization,
        name=form_name,
        schema=form_fields["schema"],
        status=form_fields.get("status", "active"),
    )
    return new_form, True, None


def _load_templates_from_fixture(
    fixtures_dir: Path,
    fixture_config: FixtureConfig,
    organization: Organization,
    demo_form: Form,
) -> tuple[int, int, list[str]]:
    created_count = 0
    updated_count = 0
    errors = []

    template_data_path = fixtures_dir / fixture_config["template_data_file"]
    if not template_data_path.exists():
        errors.append(f"Template data file not found: {template_data_path}")
        return created_count, updated_count, errors

    try:
        with template_data_path.open() as f:
            template_json = json.load(f)

        for template_obj in template_json:
            fields = template_obj["fields"]

            # Check if template already exists for this org (by name)
            existing_template = SummaryTemplate.objects.filter(
                organization=organization,
                name=fields["name"],
            ).first()

            if existing_template:
                existing_template.form = demo_form
                existing_template.description = fields["description"]
                existing_template.text = fields["text"]
                existing_template.save()
                updated_count += 1
            else:
                SummaryTemplate.objects.create(
                    organization=organization,
                    form=demo_form,
                    name=fields["name"],
                    description=fields["description"],
                    text=fields["text"],
                )
                created_count += 1

    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
        errors.append(f"Failed to load templates from {fixture_config['template_data_file']}: {e}")

    return created_count, updated_count, errors


@transaction.atomic
def create_or_update_demo_fixtures(organization: Organization, fixture_configs: list[FixtureConfig]) -> FixtureResults:
    results: FixtureResults = {
        "created_forms": 0,
        "updated_forms": 0,
        "created_templates": 0,
        "updated_templates": 0,
        "errors": [],
    }

    fixtures_dir = Path(__file__).parent.parent / "fixtures"

    for fixture_config in fixture_configs:
        demo_form, was_created, form_error = _load_form_from_fixture(fixtures_dir, fixture_config, organization)

        if form_error:
            results["errors"].append(form_error)
            continue

        if demo_form is None:
            continue

        if was_created:
            results["created_forms"] += 1
        else:
            results["updated_forms"] += 1

        created, updated, errors = _load_templates_from_fixture(fixtures_dir, fixture_config, organization, demo_form)
        results["created_templates"] += created
        results["updated_templates"] += updated
        results["errors"].extend(errors)

    return results
