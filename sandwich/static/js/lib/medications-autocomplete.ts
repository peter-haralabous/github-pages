import type { Model } from 'survey-core';

interface MedicationResult {
  drugbank_id: string;
  name: string;
  display_name: string | null;
}

interface ItemOptions {
  name: string;
  value: string;
}

async function fetchMedicationsSuggestions(
  url: string,
): Promise<MedicationResult[]> {
  try {
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error('Medcation search failed.');
    }

    let results = await res.json();
    if (!Array.isArray(results)) {
      throw new Error('Medication results malformed.');
    }
    return results;
  } catch (error) {
    console.error(
      '[medications-autocomplete] Something went wrong when fetching suggestions.',
      error,
    );
    return [];
  }
}

function medicationResultsToOptions(
  results: MedicationResult[],
): ItemOptions[] {
  return results.map((r) => {
    return {
      name: r.display_name || r.name,
      value: r.name,
    };
  });
}

export function setupMedicationsAutocomplete(
  survey: Model,
  medicationsAutocompleteUrl: string | null,
) {
  survey.onChoicesLazyLoad.add(async (_survey, options) => {
    if (
      options.question.getType() !== 'tagbox' ||
      options.question.name !== 'medication_select' ||
      options.filter === ''
    ) {
      return;
    }

    const url = `${medicationsAutocompleteUrl}?query=${encodeURIComponent(options.filter)}`;
    const data = await fetchMedicationsSuggestions(url);

    const medicationOptions = medicationResultsToOptions(data);
    options.setItems(medicationOptions, medicationOptions.length);
  });
}
