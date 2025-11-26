import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { getByLabelText, getByText } from '@testing-library/dom';
import { userEvent } from '@testing-library/user-event';
import '@testing-library/jest-dom/vitest';

import { SurveyForm } from './survey-form';
import '../survey';

/** Loads the schema script element */
function loadSchemaScript(schema?: Record<string, unknown>): HTMLScriptElement {
  // Init script containing schema
  const script = document.createElement('script');
  script.type = 'application/json';
  script.id = 'form_schema';
  script.textContent = JSON.stringify(schema);
  document.body.appendChild(script);

  return script;
}

function loadInitialDataScript(
  initialData: Record<string, unknown>,
): HTMLScriptElement {
  const script = document.createElement('script');
  script.type = 'application/json';
  script.id = 'initial_data';
  script.textContent = JSON.stringify(initialData);
  document.body.appendChild(script);

  return script;
}

function loadSurveyComponent(attributes?: Record<string, string>): SurveyForm {
  const formComponent = document.createElement('survey-form') as SurveyForm;

  const withDefaultAttributes = {
    'data-schema-id': 'form_schema',
    'data-initial-data-id': 'initial_data',
    ...attributes,
  };
  for (const [attr, value] of Object.entries(withDefaultAttributes)) {
    formComponent.setAttribute(attr, value);
  }

  document.body.appendChild(formComponent);
  return formComponent;
}

describe('SurveyForm custom element internals', () => {
  // Note: tests asserting survey-core internals, not render concerns
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

  it('shows friendly error when JSON invalid', async () => {
    // Place the script in the document and reference it by id via data-schema-id
    const script = loadSchemaScript({});
    script.textContent = '{invalid-json}';
    document.body.appendChild(script);
    const el = loadSurveyComponent();

    // Container was created and the error box shows the message
    await vi.waitFor(() => el.querySelector('[data-survey-container]'));
    const errorMsg = el.querySelector('[id$="-error-message"]');
    expect(errorMsg).not.toBeNull();
    // now that we know it exists, assert its text content
    await vi.waitFor(() =>
      expect((errorMsg as HTMLElement).textContent).toContain(
        'Failed to load form',
      ),
    );
  });

  it('shows message when no data-schema-id script present', async () => {
    // No script in the document and no data-schema-id
    const el = loadSurveyComponent();

    // Container was created and the error box shows the message
    await vi.waitFor(() => el.querySelector('[data-survey-container]'));
    const errorEl = el.querySelector('[id$="-error"]');
    // No script provided -> component should surface an error UI.
    expect(errorEl).not.toBeNull();

    await vi.waitFor(() =>
      expect((errorEl as HTMLElement).classList.contains('hidden')).toBe(false),
    );
    const errorMsg = el.querySelector('[id$="-error-message"]');
    expect(errorMsg).not.toBeNull();
    expect((errorMsg as HTMLElement).textContent).toContain(
      'Failed to load form',
    );
  });

  it('initSurvey throws when target not found', () => {
    const el = new SurveyForm();
    // do not attach to document so its internal container id won't exist in DOM
    expect(() => el.initSurvey({ title: 'x' })).toThrow(
      /\[survey-form\] initSurvey: target element not found/,
    );
  });

  it('throws when the internal container element is missing', async () => {
    const script = loadSchemaScript({ title: 'x' });
    const el = loadSurveyComponent();

    await vi.waitFor(() => el.querySelector('[data-survey-container]'));

    // remove the internal container to simulate a missing target element
    const container = el.querySelector(
      '[data-survey-container]',
    ) as HTMLElement | null;
    if (container && container.parentElement)
      container.parentElement.removeChild(container);

    // When the internal container is missing the component will show a
    // user-friendly error message instead of throwing; assert the error
    // UI is displayed.
    (el as any)._initFromSchemaId();
    const errorMsg = el.querySelector('[id$="-error-message"]');
    expect(errorMsg).not.toBeNull();
    expect((errorMsg as HTMLElement).textContent).toContain(
      'Failed to load form',
    );
  });

  it('normal flow: loads and calls render', async () => {
    // Spy on the render method of the SurveyJS Model prototype
    const renderSpy = vi.spyOn(
      (await import('survey-core')).Model.prototype,
      'render',
    );
    const script = loadSchemaScript({ title: 'Test Survey' });
    const el = loadSurveyComponent();

    await vi.waitFor(() => expect(renderSpy).toHaveBeenCalled());
  });

  it('reads data-* attributes', async () => {
    const el = loadSurveyComponent({
      'data-submit-url': '/submit-url',
      'data-complete-url': '/done',
      'data-csrf-token': 'tok-123',
    });

    // Private fields are accessible via casting in tests
    expect((el as any)._submitUrl).toBe('/submit-url');
    expect((el as any)._completeUrl).toBe('/done');
    expect((el as any)._csrfToken).toBe('tok-123');
  });

  it('calls fetch with the correct data on submit', async () => {
    const script = loadSchemaScript({ title: 'Test' });
    const survey = loadSurveyComponent({
      'data-submit-url': '/submit-url',
      'data-complete-url': '/done',
      'data-csrf-token': 'tok-123',
    });

    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: (_: string) => 'application/json' },
      json: async () => ({}),
    });
    vi.stubGlobal('fetch', fetchSpy);

    await vi.waitUntil(() => survey.querySelector('[data-survey-rendered]'));
    expect(survey.model).not.toBeNull();
    survey.model!.data = { q1: 'my-answer' };

    vi.spyOn(survey.model!, 'doComplete');

    // Simulate the user clicking "Submit"
    // We manually trigger the 'onCompleting' event
    survey.model!.doComplete();

    // Check that fetch was called with all the right information
    await vi.waitFor(() =>
      expect(fetchSpy).toHaveBeenCalledWith('/submit-url', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': 'tok-123',
        },
        body: JSON.stringify({
          q1: 'my-answer',
        }),
      }),
    );

    expect(survey.model!.completedHtml).toContain(
      'Form successfully submitted',
    );
  });

  it('does not re-submit a form that is already completed', async () => {
    const script = loadSchemaScript({ title: 'Test' });
    const survey = loadSurveyComponent({
      'data-submit-url': '/submit-url',
      'data-complete-url': '/done',
      'data-csrf-token': 'tok-123',
    });

    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: (_: string) => 'application/json' },
      json: async () => ({}),
    });
    vi.stubGlobal('fetch', fetchSpy);

    await vi.waitUntil(() => survey.querySelector('[data-survey-rendered]'));
    expect(survey.model).not.toBeNull();
    survey.model!.data = { q1: 'my-answer' };

    // Simulate the first "Submit" click
    survey.model!.doComplete();

    // Check that fetch was called the first time
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    // Check that the survey is now in a "completed" state
    await vi.waitFor(() => expect(survey.model!.state).toBe('completed'));

    // Clear the call history of our mock
    fetchSpy.mockClear();

    // Simulate the user clicking "Submit" AGAIN
    survey.model!.doComplete();

    // Check that fetch was NOT called a second time
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('does not run draft save while submit is in progress', async () => {
    const script = loadSchemaScript({ title: 'Test' });
    const survey = loadSurveyComponent({
      'data-submit-url': '/submit-url',
      'data-save-draft-url': '/save-draft',
      'data-csrf-token': 'tok-123',
    });

    // Create a submit promise we control so submit stays in-flight
    let resolveSubmit: (value?: any) => void = () => undefined;
    const submitPromise = new Promise((res) => {
      resolveSubmit = res;
    });

    const fetchSpy = vi
      .fn()
      .mockReturnValueOnce(submitPromise) // first call is the stalled submit
      .mockResolvedValue({
        ok: true,
        headers: { get: (_: string) => 'application/json' },
        json: async () => ({}),
      });
    vi.stubGlobal('fetch', fetchSpy);

    await vi.waitUntil(() => survey.querySelector('[data-survey-rendered]'));
    const model = (survey as any).model;
    expect(model).not.toBeNull();
    model.data = { q1: 'initial' };

    // Start submit (will be pending)
    model.doComplete();
    expect(fetchSpy).toHaveBeenCalledTimes(1);

    // While submit is pending, trigger a value change which normally schedules a draft save
    model.setValue('q1', 'changed-during-submit');
    expect(fetchSpy).toHaveBeenCalledTimes(1);

    // Finish the submit
    resolveSubmit({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({}),
    });
  });

  it('autosaves draft on value change', async () => {
    const el = new SurveyForm();
    el.setAttribute('data-save-draft-url', '/save-draft');
    el.setAttribute('data-csrf-token', 'tok-123');
    document.body.appendChild(el);

    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: (_: string) => 'application/json' },
      json: async () => ({}),
    });
    vi.stubGlobal('fetch', fetchSpy);

    // Allow element to render
    await el.updateComplete;

    const surveyModel = el.initSurvey({
      elements: [{ type: 'text', name: 'yourName' }],
    });

    // Trigger a value change which should schedule a debounced save
    surveyModel.setValue('yourName', 'Alice');

    // Wait a tick for the setTimeout to run
    await new Promise((r) => setTimeout(r, 0));

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(fetchSpy).toHaveBeenCalledWith('/save-draft', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': 'tok-123',
      },
      body: JSON.stringify(surveyModel.data),
    });

    document.body.removeChild(el);
  });

  it('debounces draft saves for quick successive changes (only final save)', async () => {
    const el = new SurveyForm();
    el.setAttribute('data-save-draft-url', '/save-draft');
    el.setAttribute('data-csrf-token', 'tok-123');
    document.body.appendChild(el);

    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: (_: string) => 'application/json' },
      json: async () => ({}),
    });
    vi.stubGlobal('fetch', fetchSpy);

    // Allow element to render
    await el.updateComplete;

    const surveyModel = el.initSurvey({
      elements: [{ type: 'text', name: 'yourName', title: 'Your name' }],
    });

    // Wait until the survey is rendered so we can interact with the real input
    await vi.waitUntil(() => el.querySelector('[data-survey-rendered]'));

    // Use user-event to type into the actual input and then blur, matching browser
    const user = userEvent.setup();
    const input = getByLabelText(
      document.body,
      'Your name',
    ) as HTMLInputElement;
    expect(input).not.toBeNull();

    // Simulate quick typing of two characters, then blur the field
    await user.type(input, 'A');
    await user.type(input, 'B');
    input.blur();

    // Wait for debounce/timers to run and ensure only one save happened
    await vi.waitFor(() => expect(fetchSpy).toHaveBeenCalledTimes(1));

    // Ensure the call used the latest data (both keystrokes)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/save-draft',
      expect.objectContaining({
        method: 'POST',
        credentials: 'same-origin',
        headers: expect.any(Object),
        body: JSON.stringify(surveyModel.data),
      }),
    );

    document.body.removeChild(el);
  });
});

describe('Survey form renders', () => {
  beforeEach(() => {
    // Ensure custom element isn't registered between tests
    if (!customElements.get('survey-form')) {
      // Register the element for jsdom tests. This is idempotent across runs.
      customElements.define('survey-form', SurveyForm as any);
    }
  });
  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('renders', async () => {
    const user = userEvent.setup();

    loadSchemaScript({
      title: 'Test Survey',
      elements: [{ name: 'Name', type: 'text' }],
    });
    loadSurveyComponent();

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));
    const input = getByLabelText(document.body, 'Name');
    expect(input).toBeInTheDocument();
    await user.type(input, 'test');
    expect(input).toHaveValue('test');
  });

  it('renders in read only mode', async () => {
    const user = userEvent.setup();

    loadSchemaScript({
      title: 'Test Survey',
      elements: [{ name: 'Name', type: 'text' }],
    });
    loadSurveyComponent({ readonly: '' });

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));

    const input = getByLabelText(document.body, 'Name');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('readonly');
    await user.type(input, 'test');
    expect(input).toHaveValue('');
  });

  it('renders with initial data', async () => {
    loadSchemaScript({
      title: 'Test Survey',
      elements: [{ name: 'name', title: 'Name', type: 'text' }],
    });
    loadInitialDataScript({ name: 'Tad Cooper' });
    loadSurveyComponent();

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));

    const input = getByLabelText(document.body, 'Name');
    expect(input).toBeInTheDocument();
    expect(input).toHaveValue('Tad Cooper');
  });

  it('errors on malformed data', async () => {
    loadSchemaScript({
      title: 'Test Survey',
      elements: [{ name: 'name', title: 'Name', type: 'text' }],
    });
    const dataEl = loadInitialDataScript({});
    // Override initial data to invalid JSON
    dataEl.innerText = 'invalid_JSON';
    loadSurveyComponent();

    await vi.waitFor(() => getByText(document.body, 'Test Survey'));

    await vi.waitFor(() =>
      getByText(document.body, 'Failed to load initial data: data invalid.'),
    );
  });
});
