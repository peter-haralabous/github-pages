import { LitElement, html } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { globalStyles } from './styles';

/**
 * Inline edit field component that handles both select and date inputs.
 * Supports auto-submit on change, cancel on escape, and HTMX integration.
 */
@customElement('inline-edit-field')
export class InlineEditField extends LitElement {
  static styles = [globalStyles];

  @property({ type: String, attribute: 'field-type' }) accessor fieldType = '';

  private form: HTMLFormElement | null = null;
  private isSubmitting = false;
  private abortController: AbortController | null = null;
  private changeHandled = false;
  private pendingBlurCheck: number | null = null;
  private displayTemplate: HTMLTemplateElement | null = null;

  // Render in Light DOM to work with daisy-ui & HTMX and form submission
  createRenderRoot(): HTMLElement {
    return this;
  }

  connectedCallback(): void {
    super.connectedCallback();
    this.displayTemplate = this.querySelector(
      'template[data-display-html]',
    ) as HTMLTemplateElement | null;
    requestAnimationFrame(() => this.initialize());
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this.abortController?.abort();
    if (this.pendingBlurCheck !== null) {
      cancelAnimationFrame(this.pendingBlurCheck);
      this.pendingBlurCheck = null;
    }
  }

  private initialize(): void {
    this.form = this.querySelector('form');
    if (!this.form) {
      return;
    }

    this.abortController = new AbortController();
    const { signal } = this.abortController;

    this.form.addEventListener('htmx:afterRequest', this.handleAfterRequest, {
      signal,
    });
    this.form.addEventListener('htmx:responseError', this.handleResponseError, {
      signal,
    });

    if (this.fieldType === 'select') {
      const select = this.form.querySelector('select');
      if (select instanceof HTMLSelectElement) {
        this.setupSelect(select, signal);
      }
    } else if (this.fieldType === 'date') {
      const dateInput = this.form.querySelector('input[type="date"]');
      if (dateInput instanceof HTMLInputElement) {
        this.setupDate(dateInput, signal);
      }
    }
  }

  private handleAfterRequest = (): void => {
    this.isSubmitting = false;
    this.changeHandled = false;
  };

  private handleResponseError = (): void => {
    this.isSubmitting = false;
    this.changeHandled = false;
  };

  private setupSelect(select: HTMLSelectElement, signal: AbortSignal): void {
    const originalValue = select.value;
    const shouldAutoOpen = select.dataset.autoOpen === 'true';

    select.focus({ preventScroll: true });

    if (shouldAutoOpen) {
      this.openSelectDropdown(select);
    }

    select.addEventListener(
      'keydown',
      (e) => {
        if (e.key === 'Escape') {
          e.preventDefault();
          select.value = originalValue;
          this.changeHandled = false;
          this.cancelEdit();
        }
      },
      { signal },
    );

    select.addEventListener(
      'change',
      () => {
        this.changeHandled = true;
        if (select.value !== originalValue && this.form) {
          this.submitForm(this.form);
        }
      },
      { signal },
    );

    select.addEventListener(
      'input',
      () => {
        // Input event fires during interaction - mark as handled but don't submit yet
        // Change event will submit, or blur will check the final value
        if (select.value !== originalValue) {
          this.changeHandled = true;
        }
      },
      { signal },
    );

    select.addEventListener(
      'blur',
      (e: FocusEvent) => {
        // Check if focus moved to another element within the same form/component
        if (e.relatedTarget && this.contains(e.relatedTarget as Node)) {
          return;
        }

        this.handleBlur(originalValue, select.value);
      },
      { signal },
    );
  }

  private openSelectDropdown(select: HTMLSelectElement): void {
    const maybePicker = (
      select as HTMLSelectElement & { showPicker?: () => void }
    ).showPicker;
    if (typeof maybePicker === 'function') {
      try {
        maybePicker.call(select);
      } catch {
        // Ignore picker errors - focusing is sufficient fallback
      }
    }
  }

  private setupDate(dateInput: HTMLInputElement, signal: AbortSignal): void {
    const originalValue = dateInput.value;

    dateInput.focus({ preventScroll: true });

    dateInput.addEventListener(
      'change',
      () => {
        this.changeHandled = true;
        if (
          dateInput.value !== originalValue &&
          dateInput.value !== '' &&
          this.form
        ) {
          this.submitForm(this.form);
        }
      },
      { signal },
    );

    dateInput.addEventListener(
      'blur',
      (e: FocusEvent) => {
        // Check if focus moved to another element within the same form/component
        if (e.relatedTarget && this.contains(e.relatedTarget as Node)) {
          return;
        }
        this.handleBlur(originalValue, dateInput.value);
      },
      { signal },
    );

    dateInput.addEventListener(
      'keydown',
      (e) => {
        if (e.key === 'Escape') {
          e.preventDefault();
          dateInput.value = originalValue;
          this.changeHandled = false;
          this.cancelEdit();
        } else if (e.key === 'Enter') {
          e.preventDefault();
          if (
            dateInput.value !== originalValue &&
            dateInput.value !== '' &&
            this.form
          ) {
            this.submitForm(this.form);
          } else {
            this.cancelEdit();
          }
        }
      },
      { signal },
    );
  }

  private handleBlur(originalValue: string, currentValue: string): void {
    if (this.pendingBlurCheck !== null) {
      cancelAnimationFrame(this.pendingBlurCheck);
    }

    // Use requestAnimationFrame instead of setTimeout for better timing to
    // solve the problem of blur firing before change/input events.
    // RAF ensures we check after the browser has processed all pending events
    this.pendingBlurCheck = requestAnimationFrame(() => {
      this.pendingBlurCheck = null;

      if (this.isSubmitting) {
        return;
      }

      if (currentValue !== originalValue && !this.changeHandled && this.form) {
        this.changeHandled = true;
        this.submitForm(this.form);
        return;
      }

      if (this.changeHandled) {
        return;
      }

      if (currentValue === originalValue) {
        this.cancelEdit();
      }
    });
  }

  private submitForm(form: HTMLFormElement): void {
    if (this.isSubmitting) {
      return;
    }
    this.isSubmitting = true;

    const htmx = (
      window as typeof window & {
        htmx?: {
          trigger: (element: Element, event: string | Event) => void;
        };
      }
    ).htmx;

    if (htmx && typeof htmx.trigger === 'function') {
      htmx.trigger(form, 'submit');
      return;
    }

    if (typeof form.requestSubmit === 'function') {
      form.requestSubmit();
      return;
    }

    const submitEvent = new Event('submit', {
      bubbles: true,
      cancelable: true,
    });
    if (!form.dispatchEvent(submitEvent)) {
      return;
    }
    if (!submitEvent.defaultPrevented) {
      form.submit();
    }
  }

  private cancelEdit(): void {
    if (this.isSubmitting) {
      return;
    }

    const td = this.closest('td');
    if (!td) {
      console.error('[inline-edit-field] cancelEdit aborted - no td found');
      return;
    }

    if (!this.displayTemplate) {
      console.error(
        '[inline-edit-field] cancelEdit aborted - no displayTemplate found',
      );
      return;
    }

    const displayHtml = this.displayTemplate.innerHTML.trim();

    const htmx = (
      window as typeof window & {
        htmx?: {
          swap: (
            target: Element,
            content: string,
            options: Record<string, unknown>,
          ) => void;
        };
      }
    ).htmx;

    if (htmx && typeof htmx.swap === 'function') {
      htmx.swap(td, displayHtml, { swapStyle: 'outerHTML' });
    } else {
      td.outerHTML = displayHtml;
    }
  }

  render() {
    return html`<slot></slot>`;
  }
}
