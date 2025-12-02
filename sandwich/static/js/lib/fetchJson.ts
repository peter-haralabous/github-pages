export async function fetchJson(
  input: RequestInfo,
  init?: RequestInit,
): Promise<any> {
  const defaults: RequestInit = {
    method: 'POST',
    credentials: 'same-origin',
  };

  const initWithDefaults: RequestInit = { ...defaults, ...(init || {}) };

  const res = await fetch(input, initWithDefaults);

  try {
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(
        `HTTP error ${res.status}: ${res.statusText} - ${errorText}`,
      );
    }
    return res.json();
  } catch (e) {
    console.error('[survey-form] fetchJson error:', e);
    throw e;
  }
}
