"""Tests for AI summary service."""

import pytest

from sandwich.core.service.ai_summary_service import AISummaryResponse
from sandwich.core.service.ai_summary_service import batch_generate_summaries
from sandwich.core.service.ai_summary_service import build_system_prompt
from sandwich.core.service.ai_summary_service import build_user_prompt
from sandwich.core.service.ai_summary_service import parse_ai_response
from sandwich.core.service.ai_template import AiRequest


class TestBuildSystemPrompt:
    def test_system_prompt_matches_snapshot(self, snapshot):
        """System prompt should be deterministic and match snapshot."""
        prompt = build_system_prompt()

        assert prompt == snapshot


class TestBuildUserPrompt:
    def test_single_request_matches_snapshot(self, snapshot):
        """Single request prompt should be deterministic."""
        requests = [
            AiRequest(title="Medications", prompt="List all current medications"),
        ]

        prompt = build_user_prompt(requests)

        assert prompt == snapshot

    def test_multiple_requests_matches_snapshot(self, snapshot):
        """Multiple request prompt should be deterministic with proper numbering."""
        requests = [
            AiRequest(title="Medications", prompt="Med prompt"),
            AiRequest(title="Allergies", prompt="Allergy prompt"),
            AiRequest(title="Conditions", prompt="Condition prompt"),
        ]

        prompt = build_user_prompt(requests)

        assert prompt == snapshot


class TestParseAiResponse:
    def test_index_based_mapping(self):
        """Test that sections are mapped by position/index, not by title."""
        response = AISummaryResponse(
            sections=[
                "Med summary content",
                "Allergy summary content",
            ]
        )
        requests = [
            AiRequest(title="Medications", prompt=""),
            AiRequest(title="Allergies", prompt=""),
        ]

        result = parse_ai_response(response, requests)

        assert result["Medications"] == "Med summary content"
        assert result["Allergies"] == "Allergy summary content"

    @pytest.mark.parametrize(
        ("sections", "request_count", "scenario"),
        [
            (["Med summary content"], 2, "fewer sections than requests"),
            (["Med summary", "Allergy summary", "Extra section"], 2, "more sections than requests"),
            ([], 1, "empty sections"),
        ],
    )
    def test_section_count_mismatch_raises_error(self, sections, request_count, scenario):
        """Test that section count mismatch raises ValueError for medical accuracy."""
        response = AISummaryResponse(sections=sections)
        requests = [AiRequest(title=f"Request{i}", prompt="") for i in range(request_count)]

        with pytest.raises(ValueError, match="Section count mismatch"):
            parse_ai_response(response, requests)

    def test_correct_count_with_valid_content(self):
        """Test that matching counts with valid content works correctly."""
        response = AISummaryResponse(
            sections=[
                "## Medications\n\nPatient is on Metformin 1000mg BID",
                "## Allergies\n\nPenicillin - rash",
            ]
        )
        requests = [
            AiRequest(title="Medications", prompt="List meds"),
            AiRequest(title="Allergies", prompt="List allergies"),
        ]

        result = parse_ai_response(response, requests)

        assert len(result) == 2
        assert "Metformin" in result["Medications"]
        assert "Penicillin" in result["Allergies"]


class TestBatchGenerateSummaries:
    def test_empty_requests_returns_empty_dict(self):
        result = batch_generate_summaries([])

        assert result == {}

    @pytest.mark.vcr
    @pytest.mark.django_db
    def test_patient_history_summary(self, snapshot):
        """Generate comprehensive patient history summary with VCR determinism."""
        prompt = """Please write a concise clinical narrative summary of the patient's history.
Group the information into Medical History, Social History, and Medications/Allergies.

**Medical History:**
- Past Medical History: Type 2 Diabetes Mellitus (diagnosed 2015), Hypertension (diagnosed 2018), Hyperlipidemia
- Surgeries/Procedures: Appendectomy (2010), Cholecystectomy (2019)
- Family History: Father - MI at age 62, Mother - Type 2 DM, Sister - Breast cancer

**Lifestyle & Social:**
- Smoker: Former smoker, quit 5 years ago
- Alcohol: Social drinker, 2-3 drinks per week
- Recreational Drugs: Denies
- Exercise: Yes, walks 30 minutes daily
- Education/Occupation: College graduate, works as accountant
- Family/Dependents: Married, 2 adult children

**Medications & Allergies:**
- Prescriptions: Metformin 1000mg BID, Lisinopril 20mg daily, Atorvastatin 40mg daily
- OTC/Supplements: Vitamin D 2000 IU daily, Aspirin 81mg daily
- Allergies: Penicillin (rash), Sulfa drugs (hives)"""

        requests = [AiRequest(title="Patient History Summary", prompt=prompt)]

        result = batch_generate_summaries(requests)

        assert result == snapshot

    @pytest.mark.vcr
    @pytest.mark.django_db
    def test_multiple_clinical_sections(self, snapshot):
        """Generate multiple clinical sections with VCR determinism."""
        requests = [
            AiRequest(
                title="Chief Complaint",
                prompt="Summarize: Patient presenting with chest pain, onset 2 hours ago, "
                "described as pressure-like, radiating to left arm, associated with shortness of breath",
            ),
            AiRequest(
                title="PMHx (Past Medical History)",
                prompt="List relevant conditions: Hypertension (10 years), Type 2 Diabetes (8 years), "
                "GERD (5 years), Previous MI (2020)",
            ),
            AiRequest(
                title="Medications",
                prompt="Current medications: Metoprolol 50mg BID, Metformin 1000mg BID, "
                "Atorvastatin 80mg daily, Aspirin 81mg daily, Omeprazole 20mg daily",
            ),
            AiRequest(
                title="Social History",
                prompt="Lifestyle factors: Non-smoker for 3 years (previously 1 PPD x 20 years), "
                "Occasional alcohol use, Works as construction foreman, "
                "Lives with spouse, Exercises irregularly",
            ),
        ]

        result = batch_generate_summaries(requests)

        assert result == snapshot

    @pytest.mark.vcr
    @pytest.mark.django_db
    def test_complex_medical_data_with_lists(self, snapshot):
        """Handle complex structured data with lists with VCR determinism."""
        allergy_list = """
  * Penicillin (Reaction: Anaphylaxis)
  * Shellfish (Reaction: Hives)
  * Latex (Reaction: Contact dermatitis)
"""
        prompt = f"""Summarize the patient's allergy profile:

**Documented Allergies:**
{allergy_list}

**Clinical Significance:**
Include severity assessment and clinical implications for treatment planning."""

        requests = [AiRequest(title="Allergies", prompt=prompt)]

        result = batch_generate_summaries(requests)

        assert result == snapshot
