from django.core.management.base import BaseCommand

from sandwich.core.service.ingest.extract_pdf import extract_facts_from_pdf
from sandwich.core.service.ingest.extract_text import extract_facts_from_text
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_llm


class Command(BaseCommand):
    help = "Extract facts from a PDF file or text using an LLM."

    def add_arguments(self, parser):
        parser.add_argument("input", type=str, help="Path to the PDF file or raw text input.")
        parser.add_argument(
            "--type",
            type=str,
            default="pdf",
            choices=["pdf", "text"],
            help="Input type: 'pdf' for PDF file, 'text' for raw text.",
        )
        parser.add_argument(
            "--llm",
            type=str,
            default=ModelName.CLAUDE_3_SONNET,
            choices=[m.value for m in ModelName],
            help="LLM model to use.",
        )
        parser.add_argument("--temperature", type=float, default=None, help="LLM temperature.")

    def handle(self, *args, **options):
        input_value = options["input"]
        input_type = options["type"]
        llm_name = ModelName(options["llm"])
        temperature = options["temperature"]
        patient = None
        llm_client = get_llm(llm_name, temperature=temperature)
        if input_type == "pdf":
            self.stdout.write(self.style.NOTICE(f"Extracting facts from PDF {input_value} using {llm_name}..."))
            result = extract_facts_from_pdf(input_value, llm_client, patient=patient)
        else:
            self.stdout.write(self.style.NOTICE(f"Extracting facts from text using {llm_name}..."))
            result = extract_facts_from_text(input_value, llm_client, patient=patient)
        self.stdout.write(self.style.SUCCESS(f"LLM result: {result}"))
