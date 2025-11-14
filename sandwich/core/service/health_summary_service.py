"""Health Summary Service - Generate AI summaries of patient health records."""

import logging
from collections import defaultdict
from datetime import date

from langchain_core.messages import SystemMessage

from sandwich.core.models import HealthSummary
from sandwich.core.models import Patient
from sandwich.core.models import SummaryType
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_claude_sonnet_4_5

logger = logging.getLogger(__name__)


def get_or_generate_health_summary(
    patient: Patient, summary_type: SummaryType = SummaryType.OVERVIEW
) -> HealthSummary:
    """
    Get a cached health summary or generate a new one if data has changed.

    Args:
        patient: The patient to summarize
        summary_type: Type of summary to generate

    Returns:
        HealthSummary instance (cached or newly generated)
    """
    # Compute hash of current patient data
    current_hash = HealthSummary.compute_data_hash(patient)

    # Check if we have a cached summary with this hash
    cached_summary = (
        HealthSummary.objects.filter(patient=patient, summary_type=summary_type, data_hash=current_hash)
        .order_by("-created_at")
        .first()
    )

    if cached_summary:
        logger.info(
            "Using cached health summary",
            extra={"patient_id": patient.id, "summary_id": cached_summary.id, "summary_type": summary_type},
        )
        return cached_summary

    # Generate new summary
    logger.info("Generating new health summary", extra={"patient_id": patient.id, "summary_type": summary_type})
    return _generate_health_summary(patient, summary_type, current_hash)


def _build_provenance_map(patient: Patient) -> dict[str, dict]:
    """
    Build a map of record_id -> source information for provenance.

    Returns:
        Dict mapping "type:id" -> {"source": "chat" | "document" | "provider", "date": datetime}
    """
    provenance_map = {}

    # TODO: Re-enable chat message provenance tracking when chat feature is ready
    # This will be restored from the stashed changes

    return provenance_map


def _generate_health_summary(patient: Patient, summary_type: SummaryType, data_hash: str) -> HealthSummary:
    """
    Generate a new AI health summary with provenance information.

    Args:
        patient: The patient to summarize
        summary_type: Type of summary to generate
        data_hash: Hash of the patient data (for caching)

    Returns:
        Newly created HealthSummary instance
    """
    llm = get_claude_sonnet_4_5(temperature=0.0)

    # Gather patient health records (Release 0: only Conditions, Immunizations, Practitioners)
    conditions = list(patient.condition_set.all())
    immunizations = list(patient.immunization_set.all())
    practitioners = list(patient.practitioner_set.all())

    # Build provenance map
    provenance_map = _build_provenance_map(patient)

    # Track all source record IDs
    source_record_ids = []
    for cond in conditions:
        source_record_ids.append({"type": "condition", "id": str(cond.id)})
    for imm in immunizations:
        source_record_ids.append({"type": "immunization", "id": str(imm.id)})
    for prac in practitioners:
        source_record_ids.append({"type": "practitioner", "id": str(prac.id)})

    # Build context for the LLM with provenance information
    context_parts = []

    # Group records by source
    chat_sourced = defaultdict(list)
    other_sourced = defaultdict(list)

    for cond in conditions:
        key = f"condition:{cond.id}"
        record_info = {
            "type": "condition",
            "name": cond.name,
            "onset": cond.onset,
            "status": cond.status,
        }
        if key in provenance_map:
            chat_sourced["conditions"].append(record_info)
        else:
            other_sourced["conditions"].append(record_info)

    for imm in immunizations:
        key = f"immunization:{imm.id}"
        record_info = {
            "type": "immunization",
            "name": imm.name,
            "date": imm.date,
        }
        if key in provenance_map:
            chat_sourced["immunizations"].append(record_info)
        else:
            other_sourced["immunizations"].append(record_info)

    for prac in practitioners:
        key = f"practitioner:{prac.id}"
        record_info = {
            "type": "practitioner",
            "name": prac.name,
        }
        if key in provenance_map:
            chat_sourced["practitioners"].append(record_info)
        else:
            other_sourced["practitioners"].append(record_info)

    # Build context sections
    if chat_sourced["conditions"]:
        context_parts.append("### Health Conditions (from your conversations)")
        for cond in chat_sourced["conditions"]:
            onset_str = f" (started {cond['onset']})" if cond['onset'] else ""
            status_str = f" - {cond['status']}" if cond['status'] else ""
            context_parts.append(f"- {cond['name']}{onset_str}{status_str}")

    if other_sourced["conditions"]:
        context_parts.append("\n### Health Conditions (from other sources)")
        for cond in other_sourced["conditions"]:
            onset_str = f" (started {cond['onset']})" if cond['onset'] else ""
            status_str = f" - {cond['status']}" if cond['status'] else ""
            context_parts.append(f"- {cond['name']}{onset_str}{status_str}")

    if chat_sourced["immunizations"]:
        context_parts.append("\n### Vaccinations (from your conversations)")
        for imm in chat_sourced["immunizations"]:
            date_str = f" (received {imm['date']})" if imm['date'] else ""
            context_parts.append(f"- {imm['name']}{date_str}")

    if other_sourced["immunizations"]:
        context_parts.append("\n### Vaccinations (from other sources)")
        for imm in other_sourced["immunizations"]:
            date_str = f" (received {imm['date']})" if imm['date'] else ""
            context_parts.append(f"- {imm['name']}{date_str}")

    if chat_sourced["practitioners"] or other_sourced["practitioners"]:
        context_parts.append("\n### Your Healthcare Team")
        for prac in chat_sourced["practitioners"] + other_sourced["practitioners"]:
            context_parts.append(f"- {prac['name']}")

    # Build patient demographic information
    age = None
    if patient.date_of_birth:
        today = date.today()
        age = today.year - patient.date_of_birth.year - (
            (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
        )

    patient_info = f"""### PATIENT INFORMATION

**Name:** {patient.full_name}
**Date of Birth:** {patient.date_of_birth.strftime('%Y-%m-%d') if patient.date_of_birth else 'Not provided'}
**Age:** {age if age else 'Unknown'}
**Provincial Health Card #:** {patient.phn if patient.phn else 'Not provided'}
**Province:** {patient.get_province_display() if patient.province else 'Not specified'}
**Contact:** {patient.email if patient.email else 'Not provided'}
**Date Prepared:** {date.today().strftime('%Y-%m-%d')}"""

    if not context_parts:
        # No data to summarize - show welcome message with patient info
        summary_content = f"""{patient_info}

### GETTING STARTED

Welcome! Start a conversation to add your health information. I'll help you keep track of:
- Medical conditions
- Vaccinations and immunizations
- Healthcare providers
- And more coming soon (medications, allergies, etc.)

Your health information will automatically appear here in an organized summary."""
    else:
        # Build complete data context
        full_context = f"""{patient_info}

{chr(10).join(context_parts)}"""

        # Different prompts based on summary type
        if summary_type == SummaryType.OVERVIEW:
            prompt = f"""You are creating a clean, patient-friendly health summary. Use markdown formatting for structure.

TEMPLATE TO FOLLOW:
[Include PATIENT INFORMATION section - use the exact data provided below]

### Active Conditions
[List conditions with onset dates and status - use bullet points]
[If no conditions: Omit this section]

### Vaccinations
[List recent vaccinations with dates - use bullet points]
[If no immunizations: Omit this section]

### Care Team
[List healthcare providers - use bullet points]
[If no providers: Omit this section]

PATIENT DATA:
{full_context}

INSTRUCTIONS:
1. Start directly with the PATIENT INFORMATION section (no title needed)
2. Use exactly the patient data provided - don't modify names, dates, or other details
3. Use sentence case for section headers (e.g., "Active Conditions" not "ACTIVE MEDICAL CONDITIONS")
4. Keep bullet points concise and scannable
5. Format dates as YYYY-MM-DD consistently
6. Omit any sections where no data exists
7. Use ### for all section headers (H3 level)
8. Keep the tone professional but approachable - this is for the patient to read
9. Do NOT add a notes section or metadata about data collection"""
        elif summary_type == SummaryType.FOCUSED:
            prompt = f"""Generate a focused health summary (1 paragraph) highlighting key active conditions and recent health events:

{full_context}

Emphasize actionable insights and things that require attention."""
        else:  # COMPREHENSIVE
            prompt = f"""Generate a comprehensive health summary organized by category:

{full_context}

Provide detailed information about each category, noting patterns, trends, or important relationships between conditions."""

        # Generate summary using LLM
        response = llm.invoke([SystemMessage(content=prompt)])
        # Handle response content (could be string or list of content blocks)
        if isinstance(response.content, str):
            summary_content = response.content
        else:
            # Handle list of content blocks
            summary_content = str(response.content)

    # Save to database
    health_summary = HealthSummary.objects.create(
        patient=patient,
        summary_type=summary_type,
        content=summary_content,
        data_hash=data_hash,
        model_version=ModelName.CLAUDE_SONNET_4_5,
        tokens_used=0,
        generation_time_ms=0,
        source_record_ids=source_record_ids,
    )

    logger.info(
        "Created new health summary",
        extra={
            "patient_id": patient.id,
            "summary_id": health_summary.id,
            "summary_type": summary_type,
            "content_length": len(summary_content),
            "record_count": len(source_record_ids),
        },
    )

    return health_summary
