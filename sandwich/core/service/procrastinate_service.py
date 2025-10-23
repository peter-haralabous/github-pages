import logging

from procrastinate.contrib.django import app

from sandwich.core.models.document import Document
from sandwich.core.service import invitation_service
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm
from sandwich.core.services.ingest.extract_pdf import extract_facts_from_pdf

logger = logging.getLogger(__name__)


# Tasks go here.
# https://procrastinate.readthedocs.io/en/stable/howto/basics/tasks.html
# https://procrastinate.readthedocs.io/en/stable/howto/advanced/cron.html#launch-a-task-periodically

# If the task has a better suited place, put it there instead of here.
# For Procrastinate to find your task(s), make sure that the module is
# listed in the PROCRASTINATE_IMPORT_PATHS setting or that it is in an
# autodiscovered module. By default, procrastinate looks for tasks.py
# in a django app, or is set with PROCRASTINATE_AUTODISCOVER_MODULE_NAME
# https://procrastinate.readthedocs.io/en/stable/howto/django/settings.html#customize-the-app-integration-through-settings


@app.periodic(cron="0 2 * * *")  # every day at 2am
@app.task(lock="expire_invitations_lock")
def expire_invitations_job(timestamp: int) -> None:
    expired_count = invitation_service.expire_invitations()
    logger.info("Expired %d invitations", expired_count)


@app.task
def extract_facts_from_pdf_job(document_id: str, llm_name: str = ModelName.CLAUDE_SONNET_4_5):
    document = Document.objects.get(id=document_id)
    patient = document.patient if hasattr(document, "patient") else None
    llm_client = get_llm(ModelName(llm_name))

    try:
        with document.file.open("rb") as f:
            pdf_bytes = f.read()
    except Exception:
        logger.exception("Failed to read document file", extra={"document_id": str(document_id)})
        return

    extract_facts_from_pdf(pdf_bytes, llm_client, patient=patient)
