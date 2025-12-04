import logging

from django.core.management import BaseCommand
from django.core.management import CommandParser

from sandwich.core.management.lib.logging import LoggingMixin
from sandwich.core.management.lib.subcommand import SubcommandMixin
from sandwich.core.management.types import patient_type
from sandwich.core.models import Patient
from sandwich.core.service.agent_service.memory import purge_thread


class Command(SubcommandMixin, LoggingMixin, BaseCommand):  # type: ignore[override]
    noun = "LLM"

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        self.add_subcommand(
            "chat",
            self.chat,
            arguments=[
                (("patient",), {"type": patient_type, "help": "Patient for chat context"}),
                (("--delete",), {"help": "Delete existing chat history for patient", "action": "store_true"}),
            ],
        )

    def chat(self, patient: Patient, *, delete: bool = False, **_) -> None:
        # Disable some noisy logging
        logging.getLogger("botocore.credentials").setLevel(logging.WARNING)
        logging.getLogger("langchain_aws.llms.bedrock").setLevel(logging.WARNING)
        logging.getLogger("langchain_aws.chat_models.bedrock_converse").setLevel(logging.WARNING)
        logging.getLogger("procrastinate.periodic").setLevel(logging.WARNING)

        if not patient.user:
            self.error(f"Patient {patient.id} has no associated user for chat context.")
            return

        if delete:
            thread_id = f"{patient.user.id}-{patient.id}"
            purge_thread(thread_id)
            self.info(f"Purged thread {thread_id}. History cleared.")
            return

        logging.info("Nothing to do. Use --delete to clear chat history for the patient.")
