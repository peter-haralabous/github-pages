system_prompt = """
You are diligent form generation assistant specializing in turning PDFs and
CSVs into SurveyJS form schema.
"""


def form_from_pdf(description: str | None = None) -> str:
    return f"""
    Attached is a PDF medical assessment form. Preserving it's questions and
    wording, convert it to a SurveyJS form.

    Do your best to infer whether the form needs to be single or multipage.
    Single page forms use the `elements` array at the top-level, multipage
    forms use `pages`.

    {f"Additional instructions/description of form: \n{description}" if description else ""}
    """


def form_from_csv(description: str | None = None) -> str:
    return f"""
    Attached is a CSV text document that describes a medical assessment form.
    Preserving it's questions and wording, convert the document into a
    SurveyJS form.

    Do your best to infer whether the form needs to be single or multipage.
    Single page forms use the `elements` array at the top-level, multipage
    forms use `pages`.

    {f"Additional instructions/description of form: \n{description}" if description else ""}
    """
