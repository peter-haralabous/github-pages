import pytest
from django.core.exceptions import ValidationError

from sandwich.core.validators.surveyjs_form_validator import validate_survey_json


@pytest.mark.django_db
def test_fail_is_required():
    data = {
        "title": "Type Mismatch Test",
        "pages": [{"name": "page1", "elements": [{"type": "text", "name": "q1", "isRequired": "yes"}]}],
    }

    with pytest.raises(ValidationError, match="'isRequired': 'yes'} is not valid"):
        validate_survey_json(data)


@pytest.mark.django_db
def test_fail_root_property_type_mismatch():
    data = {"showTitle": "yes"}
    with pytest.raises(ValidationError, match="'yes' is not of type 'boolean'"):
        validate_survey_json(data)


@pytest.mark.django_db
def test_fail_pages_must_be_array():
    data = {"pages": {"name": "page1"}}
    with pytest.raises(ValidationError, match="is not of type 'array'"):
        validate_survey_json(data)


@pytest.mark.django_db
def test_fail_read_only_boolean():
    data = {
        "title": "asdfasdf",
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "radiogroup",
                        "name": "question1",
                        "readOnly": "try",
                        "choices": ["Item 1", "Item 2", "Item 3"],
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError, match="'readOnly': 'try'"):
        validate_survey_json(data)


@pytest.mark.django_db
def test_fail_visible_boolean():
    data = {
        "title": "asdfasdf",
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "radiogroup",
                        "name": "question1",
                        "visible": "no",
                        "choices": ["Item 1", "Item 2", "Item 3"],
                    }
                ],
            }
        ],
    }
    with pytest.raises(ValidationError, match="'visible': 'no'"):
        validate_survey_json(data)


@pytest.mark.django_db
def test_fail_show_title():
    data = {
        "title": "asdfasdf",
        "pages": [
            {
                "name": "page1",
                "elements": [{"type": "radiogroup", "name": "question1", "choices": ["Item 1", "Item 2", "Item 3"]}],
            }
        ],
        "showTitle": "no",
    }
    with pytest.raises(ValidationError, match="'no' is not of type 'boolean'"):
        validate_survey_json(data)


@pytest.mark.django_db
def test_fail_width_mode():
    data = {
        "title": "asdfasdf",
        "pages": [
            {
                "name": "page1",
                "elements": [{"type": "radiogroup", "name": "question1", "choices": ["Item 1", "Item 2", "Item 3"]}],
            }
        ],
        "widthMode": "yes",
    }
    with pytest.raises(ValidationError, match="'yes' is not one of"):
        validate_survey_json(data)
