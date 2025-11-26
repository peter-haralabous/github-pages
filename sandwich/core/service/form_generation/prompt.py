# TODO(MM): This should extend our general system prompt
system_prompt = """
You are diligent form generation assistant specializing in turning PDFs and
CSVs into SurveyJS form schema.

You will be given file contents, use the provided tools to write the contents
to the form schema.

The order in which the form is built is important, for complex operations
requiring multiple tool calls, break the steps down and execute one at a time.
"""


def form_from_pdf(description: str | None = None) -> str:
    return f"""
    Attached is a PDF medical assessment form. Process the PDF one page at a
    time and use the tools provided to construct a SurveyJS form.

    Using the context of previous pages you may have processed and the content
    of the document, do your best to determine logical page splits.

    If the current page has content that has spilled over from the previous
    page, use the `append_elements_to_existing_page` tool.

    Preserving it's questions and wording, convert it to a SurveyJS form.

    {f"Additional instructions/description of form: \n{description}" if description else ""}
    """


def form_from_csv(description: str | None = None) -> str:
    return f"""
    Attached is a CSV text document that describes a medical assessment form.
    Preserving it's questions and wording, convert the document into a
    SurveyJS form.

    {f"Additional instructions/description of form: \n{description}" if description else ""}
    """
