import type { SurveyForm } from '../survey-form';

/** Loads the schema script element */
export function loadSchemaScript(
  schema?: Record<string, unknown>,
): HTMLScriptElement {
  // Init script containing schema
  const script = document.createElement('script');
  script.type = 'application/json';
  script.id = 'form_schema';
  script.textContent = JSON.stringify(schema);
  document.body.appendChild(script);

  return script;
}

export function loadInitialDataScript(
  initialData: Record<string, unknown>,
): HTMLScriptElement {
  const script = document.createElement('script');
  script.type = 'application/json';
  script.id = 'initial_data';
  script.textContent = JSON.stringify(initialData);
  document.body.appendChild(script);

  return script;
}

export function loadSurveyComponent(
  attributes?: Record<string, string>,
): SurveyForm {
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
