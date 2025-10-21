import json

from sandwich.core.services.ingest.schema import NODES
from sandwich.core.services.ingest.schema import PATTERNS
from sandwich.core.services.ingest.schema import RELATIONSHIPS


def get_ingest_prompt(input_text: str, input_description: str = "") -> str:
    schema = {"predicates": RELATIONSHIPS, "nodes": NODES, "patterns": PATTERNS}

    input_description_block = (
        f"""
\nThe text to analyze was described as: {input_description}\n
"""
        if input_description
        else ""
    )

    user_prompt_expansion = ""
    # Sandwich does not yet support user preferences, so skip for now

    return f"""
You are extracting structured (subject, predicate, object) triples from clinical text to create a knowledge graph.

You must structure your output according to the schema below:

 For each triple:
- Subjects and objects must be valid node types and predicates must be valid predicates.
- The relationship between `subject`, `object`, and `predicate` must be one of the allowed patterns in the schema.
- If a sentence contains multiple facts (e.g., a symptom and its cause), extract multiple triples.

Attempt to capture all clinically relevant data.

Rules for parsing:
- For observations (vital signs, tests, etc.) with multiple measurements over time, capture each recorded value as its
own (triple) to ensure we are capturing every Observation in the text.
  - for example:
      ```
        His weight has been monitored due to steroid use:
        - July 2018: 175 lbs
        - August 2019: 183 lbs
        - May 2021: 179 lbs
        - May 2025: 171 lbs
      ```
    should be captured as 4 distinct triples

- No need to extract data verbatim, try to use the most clinically valuable wording.
- Each triple must have **exactly one date value**. Do **not** group or merge dates into arrays or sets. If a fact is
observed at multiple times, **extract a separate triple for each occurrence**, each with its own object and date.
- For condition or symptom checklists or tables:
    - If a row has a checkmark or 'X' under the **No** column, the patient does **not** have that condition.
    - If the **Yes** column is checked, the patient **does** have the condition.
    - If neither is marked, skip the row.

- If the clinical fact is negated, hypothetical, or mentioned as past history, include a traits object with keys like
negation, hypothetical, or past_history, each set to true. Omit keys that are not relevant."

- If present in the text, include patient demographics on the Patient subject node:
    first_name, last_name, date_of_birth (YYYY-MM-DD), phn, email.
    Do NOT use a single "name" field for Patient. Always use "first_name" and "last_name".

Ensure the generated triples are valid according to the schema.

---

### Schema
{json.dumps(schema, indent=2)}

---

Return a JSON array like:
[
{{
    "subject": {{"entityType": "Patient", "node": {{...}}}},
    "predicate": "raw text",
    "normalized_predicate": {{"predicateType": "CANONICAL_PREDICATE", "properties": {{...}}, "traits": {{...}}}},
    "object": {{"entityType": "Condition", "node": {{...}}}},
}},
...
]

Make sure you adhere to the following rules to produce valid JSON objects:
- Do not return any additional information other than the JSON in it.
- Omit any backticks around the JSON - simply output the JSON on its own.
- Property names must be enclosed in double quotes
{input_description_block}{user_prompt_expansion}
Text to analyze:
{input_text}
"""
