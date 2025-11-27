You are creating a clean, patient-friendly health summary.
Use markdown formatting for structure.

TEMPLATE TO FOLLOW:

<template>

[Include PATIENT INFORMATION section - use the exact data provided below]

### Active Conditions
[List conditions with status: Active, Recurrence, or Relapse - use bullet points]
[Include onset dates and status]
[If no active conditions: Omit this section]

### Past Medical History
[List conditions with status: Resolved, Inactive, or Remission - use bullet points]
[Include onset and resolution dates where available]
[Conditions with status Unknown should go here as well]
[If no past conditions: Omit this section]

### Medications
[Organize by category if recognizable (e.g., Antibiotics, Pain Relief, Hormonal, Respiratory)]
[Use bullet points within each category]
[If medication details are missing, just list the name]
[If more than 15 medications, show the most relevant 15 and note "and X more"]
[If no medications: Omit this section]

### Allergies & Intolerances
[List known allergies with reactions and severity - use bullet points]
[If no allergies: Omit this section]

### Lab Results
[Group by category if recognizable (e.g., Blood Work, Metabolic Panel)]
[Include values, reference ranges, and dates - use bullet points]
[If more than 20 results, show the most recent/relevant and note "and X more"]
[If no lab results: Omit this section]

### Procedures
[List procedures with dates and locations - use bullet points]
[If no procedures: Omit this section]

### Immunizations
[List recent immunizations with dates - use bullet points]
[If no immunizations: Omit this section]

### Family History
[List conditions with relationships and age of onset - use bullet points]
[If no family history: Omit this section]

### Care Team
[Format provider names with appropriate titles (e.g., "Dr." for physicians)]
[Use bullet points]
[If more than 10 providers, show the 10 most relevant and note "and X more"]
[If no providers: Omit this section]

</template>

PATIENT DATA:

<patient-context>

{{ patient_context|safe }}

</patient-context>


INSTRUCTIONS:
1. Start directly with the PATIENT INFORMATION section (no title needed)
2. Use exactly the patient data provided - don't modify, rephrase, or reformat names, dates, or other details
3. CRITICAL: Preserve ALL markdown links exactly as provided in the source data
   - do not remove or modify any links in square brackets [text](url)
4. If you see duplicate items with the same or very similar names, list each item only once
5. For MEDICATIONS: Organize by category (Antibiotics, Pain Relief, etc.) to make scannable
6. For LAB RESULTS: Group by category when possible for better organization
7. Use sentence casing
8. Keep bullet points concise and scannable
9. Format dates as YYYY-MM-DD consistently
10. Omit any sections where no data exists
11. Use ### for all section headers (H3 level)
12. Keep the tone professional but approachable - this is for the patient to read
13. Do NOT add a notes section or metadata about data collection
