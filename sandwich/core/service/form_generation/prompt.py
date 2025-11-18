def form_from_pdf(description: str | None = None) -> str:
    return f"""
    You are a helpful assistant that converts PDF documents into JSON form
    schemas compatible with SurveyJS.

    Attached is a PDF medical assessment form. Preserving it's questions and
    wording, convert it to a SurveyJS form.

    {f"Additional instructions/description of form: \n{description}" if description else ""}
    """


def form_from_csv(description: str | None = None) -> str:
    return f"""
    You are a helpful assistant that converts CSV documents into JSON form
    schemas compatible with SurveyJS.

    Attached is a CSV text document that describes a medical assessment form.
    Preserving it's questions and wording, convert the document into a
    SurveyJS form.

    {f"Additional instructions/description of form: \n{description}" if description else ""}
    """
