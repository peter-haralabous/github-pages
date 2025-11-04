import { describe, it, expect, beforeEach, vi } from 'vitest';

import { SurveyForm } from './survey-form';

describe('SurveyForm custom element', () => {
  // Note: tests asserting survey-core internals / render calls rely
  // on E2E Playwright tests elsewhere since they depend on browser
  // behavior.

  beforeEach(() => {
    // Ensure custom element isn't registered between tests
    if (!customElements.get('survey-form')) {
      // Register the element for jsdom tests. This is idempotent across runs.
      customElements.define('survey-form', SurveyForm as any);
    }
  });

  it('shows friendly error when JSON invalid', async () => {
    const el = new SurveyForm();
    // Place the script in the document and reference it by id via data-schema-id
    const script = document.createElement('script');
    script.type = 'application/json';
    script.id = 'form_schema';
    script.textContent = '{invalid-json}';
    document.body.appendChild(script);

    el.setAttribute('data-schema-id', 'form_schema');
    document.body.appendChild(el);

    // Manually trigger connected lifecycle in JSDOM and allow the microtask tick
    el.connectedCallback();
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Container was created and the error box shows the message
    const container = el.querySelector('[data-survey-container]');
    expect(container).toBeTruthy();
    const errorMsg = el.querySelector('[id$="-error-message"]');
    expect(errorMsg).not.toBeNull();
    // now that we know it exists, assert its text content
    expect((errorMsg as HTMLElement).textContent).toContain(
      'Failed to load form',
    );

    document.body.removeChild(el);
    document.body.removeChild(script);
  });

  it('shows message when no data-schema-id script present', async () => {
    const el = new SurveyForm();
    // No script in the document and no data-schema-id -> should show the helper message
    document.body.appendChild(el);

    el.connectedCallback();
    await new Promise((r) => setTimeout(r, 0));

    // Container was created and the error box shows the message
    const container = el.querySelector('[data-survey-container]');
    expect(container).toBeTruthy();
    const errorEl = el.querySelector('[id$="-error"]');
    // No script provided -> component should surface an error UI.
    expect(errorEl).not.toBeNull();
    expect((errorEl as HTMLElement).classList.contains('hidden')).toBe(false);
    const errorMsg = el.querySelector('[id$="-error-message"]');
    expect(errorMsg).not.toBeNull();
    expect((errorMsg as HTMLElement).textContent).toContain(
      'Failed to load form',
    );

    document.body.removeChild(el);
  });

  it('initSurvey throws when target not found', () => {
    const el = new SurveyForm();
    // do not attach to document so its internal container id won't exist in DOM
    expect(() => el.initSurvey({ title: 'x' })).toThrow(
      /\[survey-form\] initSurvey: target element not found/,
    );
  });

  it('throws when the internal container element is missing', async () => {
    const el = new SurveyForm();
    const script = document.createElement('script');
    script.type = 'application/json';
    script.id = 'form_schema';
    script.textContent = JSON.stringify({ title: 'x' });
    document.body.appendChild(script);

    el.setAttribute('data-schema-id', 'form_schema');
    // attach the element so its template is stamped into the document
    document.body.appendChild(el);

    // trigger connected lifecycle and wait for the template to be stamped
    el.connectedCallback();
    await new Promise((r) => setTimeout(r, 0));

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

    document.body.removeChild(el);
    document.body.removeChild(script);
  });

  it('normal flow: loads and calls render', async () => {
    const el = new SurveyForm();
    const script = document.createElement('script');
    script.type = 'application/json';
    script.id = 'form_schema';
    script.textContent = JSON.stringify({ title: 'Test Survey' });
    document.body.appendChild(script);

    el.setAttribute('data-schema-id', 'form_schema');
    document.body.appendChild(el);

    // Spy on the render method of the SurveyJS Model prototype
    const renderSpy = vi.spyOn(
      (await import('survey-core')).Model.prototype,
      'render',
    );

    el.connectedCallback();
    await new Promise((r) => setTimeout(r, 0));

    // No explosions here

    expect(renderSpy).toHaveBeenCalled();

    document.body.removeChild(el);
    document.body.removeChild(script);
  });

  it('reads data-* attributes on connectedCallback', async () => {
    const el = new SurveyForm();
    el.setAttribute('data-submit-url', '/submit-url');
    el.setAttribute('data-complete-url', '/done');
    el.setAttribute('data-csrf-token', 'tok-123');
    document.body.appendChild(el);

    el.connectedCallback();
    await new Promise((r) => setTimeout(r, 0));

    // Private fields are accessible via casting in tests
    expect((el as any)._submitUrl).toBe('/submit-url');
    expect((el as any)._completeUrl).toBe('/done');
    expect((el as any)._csrfToken).toBe('tok-123');

    document.body.removeChild(el);
  });

  it('calls fetch with the correct data on submit', async () => {
    const el = new SurveyForm();
    el.setAttribute('data-submit-url', '/submit-url');
    el.setAttribute('data-csrf-token', 'tok-123');
    el.setAttribute('data-complete-url', '/done');
    document.body.appendChild(el);

    const fetchSpy = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal('fetch', fetchSpy);
    await el.updateComplete;
    const surveyModel = el.initSurvey({ title: 'Test' });

    const doCompleteSpy = vi.spyOn(surveyModel, 'doComplete');
    surveyModel.data = { q1: 'my-answer' };

    // Simulate the user clicking "Submit"
    // We manually trigger the 'onCompleting' event
    await surveyModel.doComplete();

    // Check that fetch was called with all the right information
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
    });

    expect(surveyModel.completedHtml).toContain('Form successfully submitted');
  });

  it('does not re-submit a form that is already completed', async () => {
    const el = new SurveyForm();
    el.setAttribute('data-submit-url', '/submit-url');
    el.setAttribute('data-csrf-token', 'tok-123');
    el.setAttribute('data-complete-url', '/done');
    document.body.appendChild(el);

    const fetchSpy = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal('fetch', fetchSpy);

    await new Promise((resolve) => setTimeout(resolve, 0));

    const surveyModel = el.initSurvey({ title: 'Test' });
    surveyModel.data = { q1: 'my-answer' };

    // Simulate the first "Submit" click
    await surveyModel.doComplete();

    // Check that fetch was called the first time
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    // Check that the survey is now in a "completed" state
    expect(surveyModel.state).toBe('completed');

    // Clear the call history of our mock
    fetchSpy.mockClear();

    // Simulate the user clicking "Submit" AGAIN
    await surveyModel.doComplete();

    // Check that fetch was NOT called a second time
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});
