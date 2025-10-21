NODES = [
    {
        "label": "Patient",
        "properties": [
            {"name": "first_name", "type": "STRING", "required": True},
            {"name": "last_name", "type": "STRING", "required": True},
            {"name": "dateOfBirth", "type": "DATE"},
            {"name": "phn", "type": "STRING"},
            {"name": "email", "type": "STRING"},
        ],
        "description": "The patient entity",
    },
    {
        "label": "Condition",
        "properties": [
            {"name": "name", "type": "STRING", "required": True},
        ],
        "description": "Clinical name of the condition.",
    },
    {
        "label": "Medication",
        "properties": [
            {
                "name": "name",
                "type": "STRING",
                "required": True,
                "description": "The clinical name of the medication.",
            },
        ],
        "description": "Medication a patient has taken or is taking.",
    },
    {
        "label": "Observation",
        "properties": [
            {
                "name": "name",
                "type": "STRING",
                "required": True,
                "description": "clinical name of the test type, symptom, imagining type, etc.",
            },
        ],
        "description": (
            "A medical observation, such as vital signs, lab results, imaging results, "
            "clinical findings, symptoms etc."
        ),
    },
    {
        "label": "AllergyIntolerance",
        "properties": [
            {
                "name": "name",
                "type": "STRING",
                "required": True,
                "description": "The substance or drug causing the allergy or intolerance.",
            },
        ],
        "description": "A reaction to a substance.",
    },
    {
        "label": "Immunization",
        "properties": [
            {
                "name": "name",
                "type": "STRING",
                "required": True,
                "description": "The name of the vaccine administered.",
            },
        ],
        "description": "A vaccine administered to the patient.",
    },
    {
        "label": "Procedure",
        "properties": [
            {
                "name": "name",
                "type": "STRING",
                "required": True,
                "description": "The clinical name of the procedure performed.",
            },
        ],
        "description": "A clinical or surgical procedure performed on the patient.",
    },
]

TRAITS = {
    "name": "traits",
    "type": "OBJECT",
    "description": (
        'Contextual flags applied to the relationship. For example: {"negation": true} if the fact was negated, '
        'or {"hypothetical": true} if uncertain. All keys should be lowercase booleans.'
    ),
    "properties": [
        {
            "name": "negation",
            "type": "BOOLEAN",
            "description": "True if the fact was explicitly negated (e.g. 'patient denies having asthma').",
        },
        {
            "name": "hypothetical",
            "type": "BOOLEAN",
            "description": "True if the fact is mentioned hypothetically (e.g. 'could develop asthma').",
        },
        {
            "name": "past_history",
            "type": "BOOLEAN",
            "description": "True if the fact refers to past history only.",
        },
    ],
}

# TODO-RG: hook this up with the constraints (`PredicateName``) defined in the Predicate model
RELATIONSHIPS = [
    {
        "label": "HAS_CONDITION",
        # "traits": TRAITS,
        "properties": [
            {
                "name": "date",
                "type": "DATE",
                "description": "Estimated or actual date the condition started",
            },
        ],
        "description": "Subject has been diagnosed with a medical condition.",
    },
    {
        "label": "TAKES_MEDICATION",
        "properties": [
            {
                "name": "quantity",
                "type": "STRING",
                "description": "The quantity of medication taken with this particular dosage.",
            },
            {"name": "unit", "type": "STRING", "description": "The unit of measurement of the medication quantity."},
            {
                "name": "form",
                "type": "STRING",
                "description": "The form of the medication (eg. tablets, capsule, powder, etc.)",
            },
            {
                "name": "frequency",
                "type": "STRING",
                "description": "How frequently the patient takes this medication.",
            },
            {"name": "date", "type": "STRING", "description": "Start date of the current regimen (if stated)"},
        ],
        "description": "Subject currently takes a medication.",
    },
    {
        "label": "HAS_LAB_RESULT",
        "properties": [
            {
                "name": "value",
                "type": "STRING",
                "required": True,
                "description": "The quantatitive value of the associated observation.",
            },
            {"name": "unit", "type": "STRING", "description": "Unit of measurement."},
            {"name": "date", "type": "STRING", "description": "When the observation was made"},
        ],
        "description": "Indicates a recorded lab result.",
    },
    {
        "label": "HAS_VITAL_SIGN",
        # "traits": TRAITS,
        "properties": [
            {
                "name": "value",
                "type": "STRING",
                "required": True,
                "description": "The quantitative value of the associated observation.",
            },
            {"name": "unit", "type": "STRING", "description": "Unit of measurement."},
            {"name": "date", "type": "STRING", "description": "When the observation was made"},
        ],
        "description": "Indicates a recorded vital sign.",
    },
    {
        "label": "HAS_SYMPTOM",
        "properties": [
            {"name": "date", "type": "STRING", "description": "When the symptom was exhibited."},
        ],
        "description": "Indicates the subject has a symptom.",
    },
    {
        "label": "HAS_ALLERGY",
        "properties": [
            {"name": "criticality", "type": "STRING", "description": "The severity of the allergy reaction."},
            {
                "name": "last_occurrence",
                "type": "DATE",
                "description": "The date of the last known occurrence of the reaction.",
            },
            {"name": "onset", "type": "DATE", "description": "When allergy or intolerance was identified"},
            {"name": "reaction", "type": "STRING", "description": "Clinical symptoms/signs associated with the Event"},
        ],
        "description": "Subject has a known allergy or intolerance.",
    },
    {
        "label": "HAS_FAMILY_HISTORY",
        "properties": [
            {
                "name": "relationship",
                "type": "STRING",
                "required": True,
                "description": "The familial relationship to the subject (e.g., 'father', 'mother').",
            },
            {"name": "name", "type": "STRING", "description": "The name of the family member."},
        ],
        "description": "Subject has a family member with a known medical history.",
    },
    {
        "label": "RECEIVED_IMMUNIZATION",
        "properties": [
            {"name": "date", "type": "DATE", "description": "The date the immunization was administered."},
            {"name": "status", "type": "STRING", "description": "The status of the immunization (e.g., 'completed')."},
            {"name": "route", "type": "STRING", "description": "Method used to administer the immunization."},
        ],
        "description": "Subject has received an immunization.",
    },
    {
        "label": "UNDERWENT_PROCEDURE",
        "properties": [
            {"name": "date", "type": "DATE", "description": "The date the procedure was performed."},
            {"name": "status", "type": "STRING", "description": "The status of the procedure (e.g., 'completed')."},
            {"name": "location", "type": "STRING", "description": "Where the procedure happened."},
            {"name": "performer", "type": "STRING", "description": "Who performed the procedure."},
        ],
        "description": "Subject underwent a clinical procedure.",
    },
]

PATTERNS = [
    ("Patient", "HAS_CONDITION", "Condition"),
    ("Patient", "TAKES_MEDICATION", "Medication"),
    ("Patient", "HAS_SYMPTOM", "Observation"),
    ("Patient", "HAS_VITAL_SIGN", "Observation"),
    ("Patient", "HAS_LAB_RESULT", "Observation"),
    ("Medication", "TAKES_FOR", "Condition"),
    ("Medication", "TAKES_FOR", "Observation"),
    ("Patient", "HAS_ALLERGY", "AllergyIntolerance"),
    ("Patient", "HAS_FAMILY_HISTORY", "Condition"),
    ("Patient", "HAS_FAMILY_HISTORY", "Observation"),
    ("Patient", "RECEIVED_IMMUNIZATION", "Immunization"),
    ("Patient", "UNDERWENT_PROCEDURE", "Procedure"),
]

PREDICATE_NAMES = [r["label"] for r in RELATIONSHIPS]  # type:ignore[index]
