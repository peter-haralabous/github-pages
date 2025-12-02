import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  loadInitialDataScript,
  loadSchemaScript,
  loadSurveyComponent,
} from './surveyFormTestUtils';
import userEvent from '@testing-library/user-event';
import { getByLabelText, getByText } from '@testing-library/dom';
import '@testing-library/jest-dom/vitest';
import { SurveyForm } from '../survey-form';
import '../../survey';

describe('medication-multi-select', () => {
  beforeEach(() => {
    // Ensure custom element isn't registered between tests
    if (!customElements.get('survey-form')) {
      // Register the element for jsdom tests. This is idempotent across runs.
      customElements.define('survey-form', SurveyForm as any);
    }
  });
  afterEach(() => {
    document.body.innerHTML = '';
    vi.clearAllMocks();
  });

  it('lazyloads results from API', async () => {
    const user = userEvent.setup();
    loadSchemaScript({
      title: 'Test Survey',
      elements: [
        {
          name: 'medications',
          title: 'Medications',
          type: 'medication-multi-select',
        },
      ],
    });
    loadSurveyComponent();

    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [
        { name: 'tylenol', display_name: 'Tylenol' },
        { name: 'tylenol extra strength' },
      ],
    });
    vi.stubGlobal('fetch', fetchSpy);

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));

    // Does not point to an input, but a container
    const medicationsContainer = getByLabelText(document.body, 'Medications');
    // Find medications input within the container
    const input: HTMLInputElement | null =
      medicationsContainer.querySelector('input');
    expect(input).toBeInTheDocument();
    await user.type(input!, 'tylen');

    await vi.waitFor(() => {
      expect(getByText(document.body, 'Tylenol')).toBeInTheDocument();
      expect(
        getByText(document.body, 'tylenol extra strength'),
      ).toBeInTheDocument();
    });
  });

  it('stores complex medication info as value', async () => {
    const user = userEvent.setup();
    loadSchemaScript({
      title: 'Test Survey',
      elements: [
        {
          name: 'medications',
          title: 'Medications',
          type: 'medication-multi-select',
        },
      ],
    });
    const surveyEl = loadSurveyComponent();

    const medicationApiData = [
      { name: 'tylenol', display_name: 'Tylenol', drugbank_id: 'drug_id1' },
      {
        name: 'acetylsalicylic acid',
        display_name: 'Aspirin',
        drugbank_id: 'drug_id2',
      },
    ];
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => medicationApiData,
    });
    vi.stubGlobal('fetch', fetchSpy);

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));

    // Does not point to an input, but a container
    const medicationsContainer = getByLabelText(document.body, 'Medications');
    // Find medications input within the container
    const input: HTMLInputElement | null =
      medicationsContainer.querySelector('input');
    expect(input).toBeInTheDocument();
    await user.type(input!, 'tylen');

    await vi.waitFor(() => {
      expect(getByText(document.body, 'Tylenol')).toBeInTheDocument();
    });
    await user.click(getByText(document.body, 'Tylenol'));
    // Selected drug value stored
    expect(surveyEl.model?.getValue('medications')).toEqual([
      medicationApiData[0],
    ]);
  });

  it('can load existing medication object value and render display value', async () => {
    const user = userEvent.setup();
    loadSchemaScript({
      title: 'Test Survey',
      elements: [
        {
          name: 'medications',
          title: 'Medications',
          type: 'medication-multi-select',
        },
      ],
    });
    loadInitialDataScript({
      // Simulate draft data or form submission
      medications: [
        {
          name: 'tylenol',
          display_name: 'Tylenol',
          drugbank_id: 'drug_id1',
        },
      ],
    });
    loadSurveyComponent();

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));

    await vi.waitFor(() => {
      expect(getByText(document.body, 'Tylenol')).toBeInTheDocument();
    });
  });

  it('displays message when the API returns no results', async () => {
    const user = userEvent.setup();
    loadSchemaScript({
      title: 'Test Survey',
      elements: [
        {
          name: 'medications',
          title: 'Medications',
          type: 'medication-multi-select',
        },
      ],
    });
    loadSurveyComponent();

    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [],
    });
    vi.stubGlobal('fetch', fetchSpy);

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));

    // Does not point to an input, but a container
    const medicationsContainer = getByLabelText(document.body, 'Medications');
    // Find medications input within the container
    const input: HTMLInputElement | null =
      medicationsContainer.querySelector('input');
    expect(input).toBeInTheDocument();
    await user.type(input!, 'no match');

    await vi.waitFor(() => {
      expect(
        getByText(document.body, 'No data to display'),
      ).toBeInTheDocument();
    });
  });
});

describe('medication-select', () => {
  beforeEach(() => {
    // Ensure custom element isn't registered between tests
    if (!customElements.get('survey-form')) {
      // Register the element for jsdom tests. This is idempotent across runs.
      customElements.define('survey-form', SurveyForm as any);
    }
  });
  afterEach(() => {
    document.body.innerHTML = '';
    vi.clearAllMocks();
  });

  it('lazyloads results from API', async () => {
    const user = userEvent.setup();
    loadSchemaScript({
      title: 'Test Survey',
      elements: [
        {
          name: 'medications',
          title: 'Medications',
          type: 'medication-select',
        },
      ],
    });
    loadSurveyComponent();

    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [
        { name: 'tylenol', display_name: 'Tylenol' },
        { name: 'tylenol extra strength' },
      ],
    });
    vi.stubGlobal('fetch', fetchSpy);

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));

    // Does not point to an input, but a container
    const medicationsContainer = getByLabelText(document.body, 'Medications');
    // Find medications input within the container
    const input: HTMLInputElement | null =
      medicationsContainer.querySelector('input');
    expect(input).toBeInTheDocument();
    await user.type(input!, 'tylen');

    await vi.waitFor(() => {
      expect(getByText(document.body, 'Tylenol')).toBeInTheDocument();
      expect(
        getByText(document.body, 'tylenol extra strength'),
      ).toBeInTheDocument();
    });
  });

  it('stores complex medication info as value', async () => {
    const user = userEvent.setup();
    loadSchemaScript({
      title: 'Test Survey',
      elements: [
        {
          name: 'medications',
          title: 'Medications',
          type: 'medication-select',
        },
      ],
    });
    const surveyEl = loadSurveyComponent();

    const medicationApiData = [
      { name: 'tylenol', display_name: 'Tylenol', drugbank_id: 'drug_id1' },
      {
        name: 'acetylsalicylic acid',
        display_name: 'Aspirin',
        drugbank_id: 'drug_id2',
      },
    ];
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => medicationApiData,
    });
    vi.stubGlobal('fetch', fetchSpy);

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));

    // Does not point to an input, but a container
    const medicationsContainer = getByLabelText(document.body, 'Medications');
    // Find medications input within the container
    const input: HTMLInputElement | null =
      medicationsContainer.querySelector('input');
    expect(input).toBeInTheDocument();
    await user.type(input!, 'tylen');

    await vi.waitFor(() => {
      expect(getByText(document.body, 'Tylenol')).toBeInTheDocument();
    });
    await user.click(getByText(document.body, 'Tylenol'));
    // Selected drug value stored
    expect(surveyEl.model?.getValue('medications')).toEqual(
      medicationApiData[0],
    );
  });

  it('can load existing medication object value and render display value', async () => {
    const user = userEvent.setup();
    loadSchemaScript({
      title: 'Test Survey',
      elements: [
        {
          name: 'medications',
          title: 'Medications',
          type: 'medication-select',
        },
      ],
    });
    loadInitialDataScript({
      // Simulate draft data or form submission
      medications: [
        {
          name: 'tylenol',
          display_name: 'Tylenol',
          drugbank_id: 'drug_id1',
        },
      ],
    });
    loadSurveyComponent();

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));

    await vi.waitFor(() => {
      expect(getByText(document.body, 'Tylenol')).toBeInTheDocument();
    });
  });

  it('displays message when the API returns no results', async () => {
    const user = userEvent.setup();
    loadSchemaScript({
      title: 'Test Survey',
      elements: [
        {
          name: 'medications',
          title: 'Medications',
          type: 'medication-select',
        },
      ],
    });
    loadSurveyComponent();

    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [],
    });
    vi.stubGlobal('fetch', fetchSpy);

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));

    // Does not point to an input, but a container
    const medicationsContainer = getByLabelText(document.body, 'Medications');
    // Find medications input within the container
    const input: HTMLInputElement | null =
      medicationsContainer.querySelector('input');
    expect(input).toBeInTheDocument();
    await user.type(input!, 'no match');

    await vi.waitFor(() => {
      expect(
        getByText(document.body, 'No data to display'),
      ).toBeInTheDocument();
    });
  });
});
