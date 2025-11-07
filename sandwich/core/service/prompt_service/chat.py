from langchain_core.prompts import ChatPromptTemplate

from sandwich.core.service.prompt_service.template import template_contents

chat_template = ChatPromptTemplate(
    [
        ("system", template_contents("system.md", "system_chat.md")),
    ]
)


def patient_context(patient):
    """Hydrate the patient context template with patient data."""
    return template_contents("patient_context.md").format(
        patient_full_name=patient.full_name,
        patient_date_of_birth=patient.date_of_birth,
        patient_province=patient.province or "Unknown",
    )


def user_context(user):
    """Hydrate the user context template with user data."""
    return template_contents("user_context.md").format(user_full_name=user.get_full_name())
