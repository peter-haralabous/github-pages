"""Tests for AI template rendering service."""

import pytest
from django.template import Context
from django.template import TemplateSyntaxError

from sandwich.core.service.ai_template import AiTemplate


class TestAiTemplateBasic:
    def test_render_without_ai_blocks_returns_template_as_is(self):
        """Test that templates without AI blocks render normally."""
        template_text = "<p>Hello {{ name }}</p>"
        template = AiTemplate(template_text)

        result = template.render({"name": "World"})

        # Note: AiTemplate prepends {% load ai_tags %} which adds a newline
        assert "Hello World" in result
        assert "<p>" in result
        assert "</p>" in result


class TestAiTemplatePromptProcessing:
    """Test that AI blocks correctly process Django template features."""

    @pytest.mark.vcr
    @pytest.mark.django_db
    def test_render_processes_django_variables_in_prompts(self, snapshot):
        """Django context variables are rendered into AI prompts deterministically."""
        template_text = """{% load ai_tags %}
{% ai "with_vars" %}
Summarize this patient information:
Patient name: {{ patient_name }}
Age: {{ age }}
{% endai %}
"""
        template = AiTemplate(template_text)

        result = template.render(
            {
                "patient_name": "John Doe",
                "age": 45,
            }
        )

        assert result == snapshot

    @pytest.mark.vcr
    @pytest.mark.django_db
    def test_render_handles_nested_template_tags_in_prompts(self, snapshot):
        """Nested Django template tags are processed deterministically in AI prompts."""
        template_text = """{% load ai_tags %}
{% ai "with_tags" %}
{% if has_conditions %}
Summarize patient conditions: {{ conditions|join:", " }}
{% else %}
No conditions to summarize
{% endif %}
{% endai %}
"""
        template = AiTemplate(template_text)

        result = template.render(
            {
                "has_conditions": True,
                "conditions": ["diabetes", "hypertension"],
            }
        )

        assert result == snapshot


class TestAiTemplateIntakeForm:
    """Test intake form scenarios with complex submission data."""

    @pytest.mark.vcr
    @pytest.mark.django_db
    def test_intake_form_with_patient_history(self, snapshot):
        """Render intake form template with patient history deterministically."""
        template_text = """# Intake Form Summary: {{ patient.first_name }} {{ patient.last_name }}

{% load ai_tags %}
{% ai "Patient History Summary" %}
Please write a concise clinical narrative summary of the patient's history based on the following intake data.
Group the information into Medical History, Social History, and Medications/Allergies.

**Medical History:**
- Past Medical History: {{ submission.data.past_medical_history }}
- Surgeries/Procedures: {{ submission.data.past_surgeries_procedures }}
- Family History: {{ submission.data.family_history }}

**Lifestyle & Social:**
- Smoker: {{ submission.data.do_you_smoke }}
- Alcohol: {{ submission.data.do_you_drink_alcohol }}
- Recreational Drugs: {{ submission.data.recreational_drugs }}
- Exercise: {{ submission.data.exercise_regularly }}
  {% if submission.data.exercise_describe %}({{ submission.data.exercise_describe }}){% endif %}
- Education/Occupation: {{ submission.data.education_occupation }}
- Family/Dependents: {{ submission.data.family_dependents }}

**Medications & Allergies:**
- Prescriptions: {{ submission.data.prescription_medications }}
- OTC/Supplements: {{ submission.data.non_prescription_medicines }}
- Allergies:{% for item in submission.data.allergies %}
  * {{ item.allergy }} (Reaction: {{ item.reaction|default:"N/A" }}){% endfor %}
{% endai %}
"""
        context = {
            "patient": {
                "first_name": "John",
                "last_name": "Smith",
            },
            "submission": {
                "data": {
                    "past_medical_history": "Type 2 Diabetes (2015), Hypertension (2018), Hyperlipidemia",
                    "past_surgeries_procedures": "Appendectomy (2010), Cholecystectomy (2019)",
                    "family_history": "Father - MI at 62, Mother - Type 2 DM",
                    "do_you_smoke": "Former smoker, quit 5 years ago",
                    "do_you_drink_alcohol": "Social, 2-3 drinks/week",
                    "recreational_drugs": "No",
                    "exercise_regularly": "Yes",
                    "exercise_describe": "Walks 30 min daily",
                    "education_occupation": "College graduate, accountant",
                    "family_dependents": "Married, 2 adult children",
                    "prescription_medications": "Metformin 1000mg BID, Lisinopril 20mg daily, Atorvastatin 40mg daily",
                    "non_prescription_medicines": "Vitamin D 2000 IU daily, Aspirin 81mg daily",
                    "allergies": [
                        {"allergy": "Penicillin", "reaction": "Rash"},
                        {"allergy": "Sulfa drugs", "reaction": "Hives"},
                    ],
                },
            },
        }

        template = AiTemplate(template_text)
        result = template.render(context)

        assert result == snapshot

    @pytest.mark.vcr
    @pytest.mark.django_db
    def test_clinical_assessment_multiple_sections(self, snapshot):
        """Render multiple clinical assessment sections deterministically."""
        template_text = """# Clinical Assessment - {{ patient.full_name }}

{% load ai_tags %}

## Demographics
- DOB: {{ patient.birthday }}
- PHN: {{ patient.phn }}

## Clinical Sections

{% ai "Chief Complaint" %}
Summarize the primary concern: {{ submission.data.chief_complaint }}
Duration: {{ submission.data.symptom_duration }}
Severity: {{ submission.data.pain_scale }}/10
{% endai %}

{% ai "HPI (History of Presenting Illness)" %}
Provide a detailed narrative of the current issue:
- Onset: {{ submission.data.symptom_onset }}
- Character: {{ submission.data.symptom_character }}
- Associated symptoms: {{ submission.data.associated_symptoms }}
- Aggravating factors: {{ submission.data.aggravating_factors }}
- Relieving factors: {{ submission.data.relieving_factors }}
- Previous treatment attempts: {{ submission.data.previous_treatment }}
{% endai %}

{% ai "PMHx (Past Medical History)" %}
List relevant chronic conditions and past illnesses:
{{ submission.data.past_medical_history }}
Previous hospitalizations: {{ submission.data.previous_hospitalizations }}
{% endai %}

{% ai "Medications" %}
List all current medications:
- Prescriptions: {{ submission.data.current_medications }}
- OTC: {{ submission.data.otc_medications }}
- Supplements: {{ submission.data.supplements }}
{% endai %}

{% ai "Social History" %}
Describe lifestyle and social factors:
- Smoking: {{ submission.data.smoking_status }}
- Alcohol: {{ submission.data.alcohol_use }}
- Occupation: {{ submission.data.occupation }}
- Living situation: {{ submission.data.living_situation }}
- Physical activity: {{ submission.data.physical_activity }}
{% endai %}
"""
        context = {
            "patient": {
                "full_name": "Jane Doe",
                "birthday": "1975-06-15",
                "phn": "9876543210",
            },
            "submission": {
                "data": {
                    "chief_complaint": "Chest pain",
                    "symptom_duration": "2 hours",
                    "pain_scale": "7",
                    "symptom_onset": "Sudden, started at rest",
                    "symptom_character": "Pressure-like, substernal",
                    "associated_symptoms": "Shortness of breath, diaphoresis, nausea",
                    "aggravating_factors": "Movement, deep breathing",
                    "relieving_factors": "None identified",
                    "previous_treatment": "Took antacid without relief",
                    "past_medical_history": "Hypertension (10 years), Type 2 DM (8 years), Hyperlipidemia (5 years)",
                    "previous_hospitalizations": "MI 2020, treated with PCI",
                    "current_medications": "Metoprolol 50mg BID, Metformin 1000mg BID, Atorvastatin 80mg QD",
                    "otc_medications": "Aspirin 81mg daily",
                    "supplements": "Vitamin D, Fish oil",
                    "smoking_status": "Former smoker, quit 3 years ago (20 pack-year history)",
                    "alcohol_use": "Occasional, 1-2 drinks per week",
                    "occupation": "Construction foreman",
                    "living_situation": "Lives with spouse",
                    "physical_activity": "Minimal due to work demands",
                },
            },
        }

        template = AiTemplate(template_text)
        result = template.render(context)

        assert result == snapshot

    @pytest.mark.vcr
    @pytest.mark.django_db
    def test_template_with_conditional_sections(self, snapshot):
        """Template with conditional AI sections renders deterministically."""
        template_text = """# Medical Summary

{% load ai_tags %}

{% if submission.data.has_allergies %}
{% ai "Allergies" %}
Document allergies with severity:
{% for allergy in submission.data.allergy_list %}
- {{ allergy.substance }}: {{ allergy.reaction }} ({{ allergy.severity }})
{% endfor %}
{% endai %}
{% endif %}

{% if submission.data.has_chronic_conditions %}
{% ai "Chronic Disease Management" %}
Summarize chronic conditions and current management:
{% for condition in submission.data.chronic_conditions %}
- {{ condition.name }}: Diagnosed {{ condition.year }}, Currently {{ condition.status }}
{% endfor %}
{% endai %}
{% endif %}

{% ai "Assessment" %}
Based on the above data, provide a clinical assessment:
- Patient age: {{ patient.age }}
- Active concerns: {{ submission.data.active_concerns }}
- Risk factors: {{ submission.data.risk_factors }}
{% endai %}
"""
        context = {
            "patient": {
                "age": 58,
            },
            "submission": {
                "data": {
                    "has_allergies": True,
                    "allergy_list": [
                        {
                            "substance": "Penicillin",
                            "reaction": "Anaphylaxis",
                            "severity": "Severe",
                        },
                        {"substance": "Shellfish", "reaction": "Urticaria", "severity": "Moderate"},
                    ],
                    "has_chronic_conditions": True,
                    "chronic_conditions": [
                        {"name": "Type 2 Diabetes", "year": "2015", "status": "Well-controlled on oral agents"},
                        {"name": "Hypertension", "year": "2018", "status": "Controlled on monotherapy"},
                    ],
                    "active_concerns": "Recent weight gain, fatigue",
                    "risk_factors": "Family history of CAD, sedentary lifestyle, elevated BMI",
                },
            },
        }

        template = AiTemplate(template_text)
        result = template.render(context)

        assert result == snapshot


class TestAiTemplateErrorHandling:
    def test_ai_tag_without_title_raises_error(self):
        template_text = """
        {% load ai_tags %}
        {% ai %}
        content
        {% endai %}
        """

        with pytest.raises(TemplateSyntaxError) as exc_info:
            AiTemplate(template_text)

        assert "requires exactly one argument" in str(exc_info.value)

    def test_ai_tag_with_unquoted_title_raises_error(self):
        template_text = """
        {% load ai_tags %}
        {% ai unquoted %}
        content
        {% endai %}
        """

        with pytest.raises(TemplateSyntaxError) as exc_info:
            AiTemplate(template_text)

        assert "must be a quoted string" in str(exc_info.value)

    def test_ai_tag_with_empty_title_raises_error(self):
        template_text = """
        {% load ai_tags %}
        {% ai "" %}
        content
        {% endai %}
        """

        with pytest.raises(TemplateSyntaxError) as exc_info:
            AiTemplate(template_text)

        assert "title cannot be empty" in str(exc_info.value)

    def test_ai_tag_without_endai_raises_error(self):
        template_text = """
        {% load ai_tags %}
        {% ai "test" %}
        content without closing tag
        """

        with pytest.raises(TemplateSyntaxError) as exc_info:
            AiTemplate(template_text)

        assert "Unclosed tag" in str(exc_info.value) or "endai" in str(exc_info.value)


class TestFindAiBlocks:
    """Test the standalone find_ai_blocks function."""

    @staticmethod
    def _find_blocks(template_text: str, context_dict: dict):
        """Helper to create template and find AI blocks."""
        template = AiTemplate(template_text)
        context = Context(context_dict)
        context.template = template
        return template.find_ai_blocks(context)

    def test_no_ai_blocks_returns_empty_list(self):
        """Templates without AI blocks return empty list."""
        result = self._find_blocks("{% load ai_tags %}<p>No AI blocks here</p>", {})

        assert result == []

    def test_single_ai_block(self):
        """Single AI block is found and extracted."""
        result = self._find_blocks(
            """{% load ai_tags %}
{% ai "Summary" %}
Generate a summary
{% endai %}""",
            {},
        )

        assert len(result) == 1
        assert result[0].title == "Summary"
        assert "Generate a summary" in result[0].prompt

    def test_multiple_ai_blocks(self):
        """Multiple AI blocks are found in order."""
        result = self._find_blocks(
            """{% load ai_tags %}
{% ai "First" %}prompt1{% endai %}
{% ai "Second" %}prompt2{% endai %}
{% ai "Third" %}prompt3{% endai %}""",
            {},
        )

        assert len(result) == 3
        assert result[0].title == "First"
        assert result[0].prompt == "prompt1"
        assert result[1].title == "Second"
        assert result[1].prompt == "prompt2"
        assert result[2].title == "Third"
        assert result[2].prompt == "prompt3"

    def test_nested_ai_blocks_in_control_structures(self):
        """AI blocks nested in conditionals and loops are found via AST traversal."""
        result = self._find_blocks(
            """{% load ai_tags %}
{% if condition %}
{% ai "If Block" %}if content{% endai %}
{% else %}
{% ai "Else Block" %}else content{% endai %}
{% endif %}
{% for item in items %}
{% ai "Loop Block" %}loop content{% endai %}
{% endfor %}""",
            {"condition": True, "items": ["a"]},
        )

        # AST traversal finds all blocks regardless of runtime execution
        assert len(result) == 3
        assert result[0].title == "If Block"
        assert result[1].title == "Else Block"
        assert result[2].title == "Loop Block"

    def test_django_variables_in_prompt(self):
        """Django template variables in prompts are rendered."""
        result = self._find_blocks(
            """{% load ai_tags %}
{% ai "Patient Summary" %}
Patient: {{ patient_name }}
Age: {{ age }}
{% endai %}""",
            {"patient_name": "John Doe", "age": 45},
        )

        assert len(result) == 1
        assert "Patient: John Doe" in result[0].prompt
        assert "Age: 45" in result[0].prompt

    def test_django_filters_in_prompt(self):
        """Django template filters in prompts are applied."""
        result = self._find_blocks(
            """{% load ai_tags %}
{% ai "List Summary" %}
Items: {{ items|join:", " }}
{% endai %}""",
            {"items": ["apple", "banana", "cherry"]},
        )

        assert len(result) == 1
        assert "Items: apple, banana, cherry" in result[0].prompt

    def test_nested_django_tags_in_prompt(self):
        """Nested Django template tags in prompts are processed."""
        result = self._find_blocks(
            """{% load ai_tags %}
{% ai "Conditional Prompt" %}
{% if has_data %}
Data: {{ data }}
{% else %}
No data available
{% endif %}
{% endai %}""",
            {"has_data": True, "data": "test data"},
        )

        assert len(result) == 1
        assert "Data: test data" in result[0].prompt
        assert "No data available" not in result[0].prompt

    def test_deeply_nested_ai_blocks(self):
        """AI blocks nested multiple levels deep are found."""
        result = self._find_blocks(
            """{% load ai_tags %}
{% if outer %}
  {% if middle %}
    {% if inner %}
      {% ai "Deep Block" %}deeply nested{% endai %}
    {% endif %}
  {% endif %}
{% endif %}""",
            {"outer": True, "middle": True, "inner": True},
        )

        assert len(result) == 1
        assert result[0].title == "Deep Block"

    def test_mixed_content_with_ai_blocks(self):
        """AI blocks mixed with regular template content are found."""
        result = self._find_blocks(
            """{% load ai_tags %}
<h1>Title</h1>
<p>Regular content</p>
{% ai "Section 1" %}ai content 1{% endai %}
<p>More regular content</p>
{% ai "Section 2" %}ai content 2{% endai %}
<footer>Footer</footer>""",
            {},
        )

        assert len(result) == 2
        assert result[0].title == "Section 1"
        assert result[1].title == "Section 2"

    def test_whitespace_handling(self):
        """Whitespace in prompts is stripped."""
        result = self._find_blocks(
            """{% load ai_tags %}
{% ai "Test" %}

    Content with whitespace

{% endai %}""",
            {},
        )

        assert len(result) == 1
        # Whitespace should be stripped
        assert result[0].prompt == "Content with whitespace"
