import { LitElement, html, type TemplateResult } from 'lit';
import { Model } from 'survey-core';
import { LayeredLightPanelless } from 'survey-core/themes';

type SurveyJson = Record<string, unknown> | Array<unknown>;

export class SurveyForm extends LitElement {
  private _containerId = `survey-form-${Math.random().toString(36).slice(2, 9)}-container`;

  createRenderRoot(): HTMLElement {
    return this as unknown as HTMLElement;
  }

  render(): TemplateResult {
    return html`
      <div id="${this._containerId}" data-survey-container="1"></div>
      <div
        id="${this._containerId}-loading"
        class="flex flex-col items-center justify-center p-6 space-y-3 mt-6"
        aria-hidden="true"
        role="status"
        aria-live="polite"
      >
        <div
          class="w-10 h-10 rounded-full border-4 border-gray-200 border-t-gray-600 animate-spin"
          aria-hidden="true"
        ></div>
        <div class="text-sm text-gray-700">
          Loading form, this should not take long...
        </div>
        <span class="sr-only">Loading form</span>
      </div>
      <div
        id="${this._containerId}-error"
        class="hidden flex items-center justify-center p-6 mt-6 border border-red-200 bg-red-50 text-red-700 rounded min-h-28"
        role="alert"
        aria-live="assertive"
      >
        <div id="${this._containerId}-error-message" class="text-sm m-0"></div>
        <span class="sr-only">Form load error</span>
      </div>
    `;
  }

  connectedCallback(): void {
    super.connectedCallback();
    this.updateComplete.then(() => void this._initFromSchemaId());
  }

  /** Hide the loading element for this component. Throws if the element is missing. */
  private setLoadingHidden(): void {
    const loadingEl = this.ownerDocument.getElementById(
      `${this._containerId}-loading`,
    ) as HTMLElement | null;
    if (!loadingEl) {
      throw new Error(
        `[survey-form] setLoadingHidden: loading element not found: ${this._containerId}-loading`,
      );
    }
    loadingEl.classList.add('hidden');
  }

  /** Show an error box with the provided message and hide the loading UI. */
  private showError(message: string): void {
    // Ensure loading is hidden first
    try {
      this.setLoadingHidden();
    } catch (e) {
      // ignore if loading element missing in odd test environments
    }
    const errorEl = this.ownerDocument.getElementById(
      `${this._containerId}-error`,
    ) as HTMLElement | null;
    const errorMsg = this.ownerDocument.getElementById(
      `${this._containerId}-error-message`,
    ) as HTMLElement | null;
    if (errorEl && errorMsg) {
      errorMsg.textContent = message;
      errorEl.classList.remove('hidden');
    }
  }

  /** Locate the schema script by id from `data-schema-id`. */
  private _findSchemaScriptById(): HTMLScriptElement | null {
    const attr = this.getAttribute('data-schema-id');
    if (!attr) return null;
    const el = this.ownerDocument.getElementById(
      attr,
    ) as HTMLScriptElement | null;
    if (
      el &&
      el.tagName.toLowerCase() === 'script' &&
      el.type === 'application/json'
    ) {
      return el;
    }
    return null;
  }

  // Initialize and render the Survey model into this component's container.
  initSurvey(json: SurveyJson): Model {
    // Resolve the target element once and fail fast if it's missing.
    const targetEl = document.getElementById(
      this._containerId,
    ) as HTMLElement | null;
    if (!targetEl) {
      throw new Error(
        `[survey-form] initSurvey: target element not found: ${this._containerId}`,
      );
    }

    // SurveyJS Model expects a loosely-typed config; cast from our safer
    // SurveyJson to `any` for the library boundary.
    const model = new Model(json as any);

    model.onAfterRenderSurvey.add(() => {
      targetEl.setAttribute('data-survey-rendered', '1');
      this.setLoadingHidden();
    });

    // TODO(JL): create and set a Thrive specific theme
    model.applyTheme(LayeredLightPanelless);

    // Render the survey into the target element
    model.render(targetEl);

    return model;
  }

  private _initFromSchemaId(): void {
    const script = this._findSchemaScriptById();
    if (!this.id)
      this.id = `survey-form-${Math.random().toString(36).slice(2, 9)}`;

    const container = this.ownerDocument.getElementById(
      this._containerId,
    ) as HTMLElement | null;
    if (!container) {
      this.showError('Failed to load form.');
      return;
    }

    let schema: SurveyJson | null = null;

    if (!script) {
      this.showError('Failed to load form: no schema found.');
      return;
    }

    try {
      schema = JSON.parse(script.textContent || '{}') as SurveyJson;
    } catch (e) {
      this.showError('Failed to load form: invalid schema.');
      return;
    }

    this.initSurvey(schema as SurveyJson);
  }
}
