import { vi, beforeEach, test, expect } from 'vitest';

// Minimal DOM the module expects
const initialScriptJSON = JSON.stringify({ title: 'Initial' });

beforeEach(() => {
  document.body.innerHTML = `
        <div id="form-builder-container"></div>
        <script id="environment" type="application/json">{}</script>
        <script id="form_schema" type="application/json">${initialScriptJSON}</script>
    `;
});

// Use the real SurveyCreator but stub slk() in survey-core to avoid license calls.
vi.mock('survey-core', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...(actual as any),
    // noop the license function so tests don't require a key
    slk: () => {},
  };
});

test('form-builder module renders real creator and updates on script change', async () => {
  // Import the module which installs DOMContentLoaded handler
  await import('./form-builder');
  document.dispatchEvent(new Event('DOMContentLoaded'));

  const container = document.getElementById('form-builder-container')!;

  // Wait until the real creator has rendered into the container
  await vi.waitFor(() =>
    expect(container.childElementCount).toBeGreaterThan(0),
  );

  expect(container.innerHTML).toContain('Your form is empty');

  const before = container.innerHTML;

  // Mutate the script content
  const script = document.getElementById('form_schema')!;
  script.textContent = JSON.stringify({ title: 'Forms have titles too' });

  // Wait for mutation observer to update the creator; expect container to change
  await vi.waitFor(() => expect(container.innerHTML).not.toBe(before));

  await vi.waitFor(() => {
    const creator = (window as any).SurveyCreator;
    expect(creator).toBeTruthy();
    expect(creator.text).toContain('Forms have titles too');
    expect(creator.text).not.toContain('Your form is empty');
  });
});

test('shows error detail in notification when save fails', async () => {
  // Setup DOM with required attributes
  const container = document.getElementById('form-builder-container')!;
  container.setAttribute('data-form-save-url', '/api/save-form');

  // Mock fetch to return an error response
  global.fetch = vi.fn().mockResolvedValue({
    ok: false,
    json: () => Promise.resolve({ detail: 'Custom error message' }),
  });

  // Import and initialize
  await import('./form-builder');
  document.dispatchEvent(new Event('DOMContentLoaded'));

  // Wait for creator to be available
  await vi.waitFor(() => expect((window as any).SurveyCreator).toBeTruthy());

  const creator = (window as any).SurveyCreator;

  // Mock the notify method to capture calls
  const notifySpy = vi.fn();
  creator.notify = notifySpy;

  // Trigger save
  const saveCallback = vi.fn();
  creator.saveSurveyFunc(1, saveCallback);

  // Wait for async error handling
  await vi.waitFor(() => {
    expect(notifySpy).toHaveBeenCalledWith('Custom error message', 'error');
    expect(saveCallback).toHaveBeenCalledWith(1, false);
  });
});
