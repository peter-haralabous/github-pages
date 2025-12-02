import type { Model } from 'survey-core';

/** The values we're parsing from the drugbank response. */
interface MedicationResult {
  drugbank_id: string;
  name: string;
  display_name: string | null;
}

/**
 * NB: By default, SurveyJS wants multi-select "tagbox" components to store
 * their values as flat arrays of strings. Since we have more complex metadata
 * about medication we want to capture, we are breaking convention and
 * storing the MedicationResult object as `value`.
 *
 * Because of this we need to use the `onGetChoiceDisplayValue` event handler
 * below to set the display value from this object when loading values from
 * an existing form submission or draft.
 */
interface MedicationSelectItemOptions {
  text: string;
  value: MedicationResult;
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
): MedicationSelectItemOptions[] {
  return results.map((r) => {
    return {
      // Not all drugbank entries have display_name
      text: r.display_name || r.name,
      value: r,
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

  /*
   * Parses a display value from our custom medication select value storage
   * object. This is necessary since we lose display text context after saving
   * the value object to the form submission.
   *
   * Since we're using a custom value object, we can persist the display text
   * as well as custom medication metadata.
   */
  survey.onGetChoiceDisplayValue.add((_survey, options) => {
    if (
      options.question.getType() !== 'tagbox' ||
      options.question.name !== 'medication_select'
    ) {
      return;
    }

    const displayValues = options.values.map((r: MedicationResult) => {
      // Not all drugbank entries have display_name
      return r.display_name || r.name;
    });

    options.setItems(displayValues);
  });
}
