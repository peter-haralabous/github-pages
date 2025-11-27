import type { Model } from 'survey-core';

/**
 * Fetches address suggestions from the provided URL.
 * @param url The endpoint URL to fetch address suggestions from
 * @param onloadSuccessCallback Callback invoked with the address data on success
 */
export async function fetchAddressSuggestions(
  url: string,
  onloadSuccessCallback: (data: Array<string>) => void,
): Promise<void> {
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    if (response.ok) {
      const data = await response.json();
      onloadSuccessCallback(data);
    }
  } catch (error) {
    console.error(
      '[address-autocomplete] fetchAddressSuggestions error:',
      error,
    );
  }
}

/**
 * Sets up address autocomplete for a Survey instance.
 * Registers a lazy load handler for the 'suggested_addresses' dropdown question.
 * @param survey The Survey instance to configure
 * @param addressAutocompleteUrl The URL endpoint for address autocomplete
 */
export function setupAddressAutocomplete(
  survey: Model,
  addressAutocompleteUrl: string | null,
): void {
  survey.onChoicesLazyLoad.add((_: any, options: any) => {
    if (options.question.getType() !== 'dropdown') return;

    // LazyLoad Choices for Address Autocomplete
    // https://surveyjs.io/form-library/examples/lazy-loading-dropdown/vanillajs#content-code
    // https://surveyjs.answerdesk.io/ticket/details/t16719/autocomplete-choicesbyurl-based-on-entered-text
    if (options.question.name === 'suggested_addresses') {
      if (!addressAutocompleteUrl) {
        console.warn('No address autocomplete URL configured.');
        return;
      }

      if (options.filter) {
        const url = `${addressAutocompleteUrl}?query=${encodeURIComponent(options.filter)}`;
        void fetchAddressSuggestions(url, (data) => {
          if (data.length) {
            options.setItems(data, data.length);
          }
        });
      }
    }
  });
}
