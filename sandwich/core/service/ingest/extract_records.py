import datetime
import logging
from typing import cast

import pghistory
import pydantic
from langchain_core.messages import SystemMessage

from sandwich.core.models import Condition
from sandwich.core.models import Document
from sandwich.core.models import Immunization
from sandwich.core.models import Practitioner
from sandwich.core.models.condition import ConditionStatus
from sandwich.core.models.document import DocumentCategory
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_claude_sonnet_4_5

logger = logging.getLogger(__name__)


class ConditionRecord(pydantic.BaseModel):
    name: str
    status: ConditionStatus | None
    onset: datetime.date | None
    abatement: datetime.date | None


class ImmunizationRecord(pydantic.BaseModel):
    name: str
    date: datetime.date


class PractitionerRecord(pydantic.BaseModel):
    name: str


class RecordsResponse(pydantic.BaseModel):
    document_category: DocumentCategory | None
    """The type of document. Infer from the title or content."""

    document_date: datetime.date | None
    """The primary date of the document (e.g., visit date, report date, or when the document was generated)."""

    conditions: list[ConditionRecord]
    immunizations: list[ImmunizationRecord]
    practitioners: list[PractitionerRecord]

    def __len__(self):
        return len(self.immunizations) + len(self.practitioners) + len(self.conditions)

    def update_document(self, document: Document) -> bool:
        changed = False
        if self.document_category and self.document_category != document.category:
            logger.debug("Updating document category", extra={"category": self.document_category})
            document.category = self.document_category
            changed = True
        if self.document_date is not None and self.document_date != document.date:
            logger.debug("Updating document date")  # extra={"date": self.document_date} breaks logging!
            document.date = self.document_date
            changed = True
        if changed:
            document.unattested = True
        return changed


content_type_to_format = {
    "text/plain": "txt",
    "application/pdf": "pdf",
}


def _to_document_block(document: Document) -> dict:
    """
    convert a Document into something that Bedrock can understand

    see https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_DocumentBlock.html
    """
    # TODO: if the file is S3-backed, pass the S3 location instead
    with document.file.open("rb") as f:
        content = f.read()
    source = {"bytes": content}

    return {
        "type": "document",
        "document": {
            # NOTE: AWS recommends not using the original filename to avoid prompt injection
            "name": "document",
            "source": source,
            # "citations": {"enabled": True},
            # "context": "something about this document",
            "format": content_type_to_format[document.content_type],
        },
    }


def _extract_records(document: Document) -> RecordsResponse:
    llm = get_claude_sonnet_4_5(temperature=0.0)
    return cast(
        "RecordsResponse",
        llm.with_structured_output(RecordsResponse).invoke(
            [
                SystemMessage(
                    content="You are a helpful assistant that extracts medical records from clinical documents."
                ),
                {
                    "role": "user",
                    "content": [
                        _to_document_block(document),
                        {
                            "type": "text",
                            "text": "Extract medical records from the above clinical document.",
                        },
                    ],
                },
            ]
        ),
    )


def _save_records(document: Document, records: RecordsResponse) -> None:
    patient = document.patient

    # Count records before saving
    conditions_before = Condition.objects.filter(patient=patient).count()
    immunizations_before = Immunization.objects.filter(patient=patient).count()
    practitioners_before = Practitioner.objects.filter(patient=patient).count()

    logger.info(
        "Starting record ingestion",
        extra={
            "document_id": document.id,
            "patient_id": patient.id,
            "conditions_before": conditions_before,
            "immunizations_before": immunizations_before,
            "practitioners_before": practitioners_before,
        },
    )

    conditions_created = 0
    immunizations_created = 0
    practitioners_created = 0

    with pghistory.context(llm=ModelName.CLAUDE_SONNET_4_5, document=document.id):
        for condition_data in records.conditions:
            # TODO: update onset/abatement dates if the record already exists
            _, created = Condition.objects.get_or_create(
                patient=document.patient,
                name__iexact=condition_data.name,
                defaults={
                    "name": condition_data.name,
                    "status": condition_data.status,
                    "onset": condition_data.onset,
                    "abatement": condition_data.abatement,
                    "unattested": True,
                },
            )
            if created:
                conditions_created += 1

        for immunization_data in records.immunizations:
            _, created = Immunization.objects.get_or_create(
                patient=document.patient,
                name__iexact=immunization_data.name,
                date=immunization_data.date,
                defaults={
                    "name": immunization_data.name,
                    "unattested": True,
                },
            )
            if created:
                immunizations_created += 1

        for practitioner_data in records.practitioners:
            _, created = Practitioner.objects.get_or_create(
                patient=document.patient,
                name__iexact=practitioner_data.name,
                defaults={
                    "name": practitioner_data.name,
                    "unattested": True,
                },
            )
            if created:
                practitioners_created += 1

        if records.update_document(document):
            document.save()

    # Count records after saving
    conditions_after = Condition.objects.filter(patient=patient).count()
    immunizations_after = Immunization.objects.filter(patient=patient).count()
    practitioners_after = Practitioner.objects.filter(patient=patient).count()

    logger.info(
        "Completed record ingestion",
        extra={
            "document_id": document.id,
            "patient_id": patient.id,
            "conditions_created": conditions_created,
            "conditions_before": conditions_before,
            "conditions_after": conditions_after,
            "immunizations_created": immunizations_created,
            "immunizations_before": immunizations_before,
            "immunizations_after": immunizations_after,
            "practitioners_created": practitioners_created,
            "practitioners_before": practitioners_before,
            "practitioners_after": practitioners_after,
            "total_records_created": conditions_created + immunizations_created + practitioners_created,
        },
    )


def extract_records(document: Document) -> RecordsResponse:
    records = _extract_records(document)
    _save_records(document, records)
    return records
