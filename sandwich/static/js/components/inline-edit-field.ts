import { LitElement, html } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import Choices from 'choices.js';

interface FieldHandler {
  setup(signal: AbortSignal): void;
  cleanup(): void;
}

abstract class BaseFieldHandler<T extends HTMLElement> implements FieldHandler {
  protected readonly element: T;
  protected readonly originalValue: string;
  protected readonly onSubmit: () => void;
  protected readonly onCancel: () => void;
  protected readonly onValueChange: (changed: boolean) => void;

  constructor(
    element: T,
    onSubmit: () => void,
    onCancel: () => void,
    onValueChange: (changed: boolean) => void,
  ) {
    this.element = element;
    this.originalValue = this.getValue();
    this.onSubmit = onSubmit;
    this.onCancel = onCancel;
    this.onValueChange = onValueChange;
  }

  setup(signal: AbortSignal): void {
    this.element.focus({ preventScroll: true });

    this.setupCustomBehavior(signal);

    this.element.addEventListener('keydown', this.handleKeydown, { signal });
    this.element.addEventListener('blur', this.handleBlur, { signal });

    if (this.shouldHandleChangeEvent()) {
      this.element.addEventListener('change', this.handleChange, { signal });
    }
  }

  cleanup(): void {
    // Cleanup is handled by AbortSignal
  }

  protected abstract getValue(): string;

  protected abstract setValue(value: string): void;

  protected setupCustomBehavior(_signal: AbortSignal): void {
    // Override in subclasses for custom setup logic
  }

  protected shouldHandleChangeEvent(): boolean {
    // Override to return false if change event should not trigger submit
    return true;
  }

  protected shouldSubmitOnChange(): boolean {
    return this.getValue() !== this.originalValue;
  }

  private readonly handleKeydown = (e: KeyboardEvent): void => {
    if (e.key === 'Escape') {
      e.preventDefault();
      this.setValue(this.originalValue);
      this.onValueChange(false);
      this.onCancel();
    }
    this.onKeydown(e);
  };

  protected onKeydown(_e: KeyboardEvent): void {
    // Override in subclasses for custom keydown handling
  }

  private readonly handleChange = (): void => {
    this.onValueChange(true);
    if (this.shouldSubmitOnChange()) {
      this.onSubmit();
    }
  };

  private readonly handleBlur = (e: FocusEvent): void => {
    const relatedTarget = e.relatedTarget as Node | null;
    const form =
      this.element instanceof HTMLInputElement ||
      this.element instanceof HTMLSelectElement
        ? this.element.form
        : null;

    if (relatedTarget && form?.contains(relatedTarget)) {
      return;
    }

    if (this.getValue() !== this.originalValue) {
      this.onSubmit();
    } else {
      this.onCancel();
    }
  };
}

class SelectFieldHandler implements FieldHandler {
  private readonly element: HTMLSelectElement;
  private readonly originalValue: string;
  private readonly onSubmit: () => void;
  private readonly onCancel: () => void;
  private readonly onValueChange: (changed: boolean) => void;
  private readonly isMultiple: boolean;
  private choicesInstance: Choices | null = null;

  constructor(
    element: HTMLSelectElement,
    onSubmit: () => void,
    onCancel: () => void,
    onValueChange: (changed: boolean) => void,
  ) {
    this.element = element;
    this.isMultiple = element.hasAttribute('multiple');
    this.originalValue = this.getValue();
    this.onSubmit = onSubmit;
    this.onCancel = onCancel;
    this.onValueChange = onValueChange;
  }

  setup(signal: AbortSignal): void {
    const searchEnabled = this.element.options.length > 10;

    this.choicesInstance =
      (this.element as any).choices ||
      new Choices(this.element, {
        removeItemButton: this.isMultiple,
        searchEnabled,
        shouldSort: false,
        itemSelectText: '',
      });

    // Auto-open dropdown after Choices is fully initialized
    requestAnimationFrame(() => {
      this.choicesInstance?.showDropdown();
      this.choicesInstance?.containerOuter?.element?.focus?.({
        preventScroll: true,
      });
    });

    this.element.addEventListener('change', this.handleChange, { signal });

    // Add keydown listener to the container for consistent keyboard handling
    if (this.choicesInstance) {
      const container = this.choicesInstance.containerOuter.element;
      container.addEventListener('keydown', this.handleKeydown, { signal });
    }

    document.addEventListener('click', this.handleClickOutside, {
      signal,
      capture: true,
    });
  }

  cleanup(): void {
    if (this.choicesInstance) {
      this.choicesInstance.destroy();
      this.choicesInstance = null;
    }
  }

  private getValue(): string {
    if (this.isMultiple) {
      const selected = Array.from(this.element.selectedOptions).map(
        (option) => option.value,
      );
      return selected.join(',');
    }
    return this.element.value;
  }

  private setValue(value: string): void {
    if (this.isMultiple) {
      const values = value ? value.split(',') : [];

      if (this.choicesInstance) {
        this.choicesInstance.removeActiveItems();
        this.choicesInstance.setChoiceByValue(values);
      } else {
        Array.from(this.element.options).forEach((option) => {
          option.selected = values.includes(option.value);
        });
      }
    } else {
      if (this.choicesInstance) {
        this.choicesInstance.setChoiceByValue(value);
      } else {
        this.element.value = value;
      }
    }
  }

  private readonly handleChange = (): void => {
    const currentValue = this.getValue();
    if (currentValue !== this.originalValue) {
      this.onValueChange(true);
      if (!this.isMultiple) {
        this.onSubmit();
      }
    }
  };

  private readonly handleClickOutside = (e: MouseEvent): void => {
    const target = e.target as Node;
    const choicesWrapper = this.element.closest('.choices');

    if (choicesWrapper && !choicesWrapper.contains(target)) {
      this.handleBlur();
    }
  };

  private handleBlur(): void {
    requestAnimationFrame(() => {
      if (this.getValue() !== this.originalValue) {
        this.onSubmit();
      } else {
        this.onCancel();
      }
    });
  }

  private readonly handleKeydown = (e: KeyboardEvent): void => {
    if (e.key === 'Escape') {
      e.preventDefault();
      e.stopPropagation();

      this.setValue(this.originalValue);
      this.onValueChange(false);

      requestAnimationFrame(() => {
        this.onCancel();
      });
    } else if (e.key === 'Enter') {
      e.preventDefault();

      if (this.getValue() !== this.originalValue) {
        this.onValueChange(true);
        requestAnimationFrame(() => {
          this.onSubmit();
        });
      }
    }
  };
}

class DateFieldHandler extends BaseFieldHandler<HTMLInputElement> {
  private lastKeyPressed: string | null = null;

  protected getValue(): string {
    return this.element.value;
  }

  protected setValue(value: string): void {
    this.element.value = value;
  }

  protected shouldHandleChangeEvent(): boolean {
    // Don't use base class change handler - we have custom logic
    return false;
  }

  protected setupCustomBehavior(signal: AbortSignal): void {
    this.element.addEventListener(
      'keydown',
      (e) => {
        if (e.key !== 'Enter' && e.key !== 'Escape') {
          this.lastKeyPressed = e.key;
        }
      },
      { signal },
    );

    // Custom change handler that only submits on calendar picker selection
    this.element.addEventListener(
      'change',
      () => {
        // If a key was pressed, just mark as changed; otherwise, auto-submit
        const shouldAutoSubmit =
          this.lastKeyPressed == null && this.shouldSubmitOnChange();
        this.onValueChange(true);
        if (shouldAutoSubmit) {
          this.onSubmit();
        }
        this.lastKeyPressed = null;
      },
      { signal },
    );
  }

  protected shouldSubmitOnChange(): boolean {
    return (
      this.element.value !== this.originalValue && this.element.value !== ''
    );
  }

  protected onKeydown(e: KeyboardEvent): void {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (this.shouldSubmitOnChange()) {
        this.onValueChange(true);
        this.onSubmit();
      } else {
        this.onCancel();
      }
    }
  }
}

/**
 * Inline edit field component that handles select, multi-select, and date inputs.
 * Supports auto-submit on change, cancel on escape, and HTMX integration.
 */
@customElement('inline-edit-field')
export class InlineEditField extends LitElement {
  @property({ type: String, attribute: 'field-type' }) accessor fieldType = '';

  private form: HTMLFormElement | null = null;
  private isSubmitting = false;
  private abortController: AbortController | null = null;
  private changeHandled = false;
  private displayTemplate: HTMLTemplateElement | null = null;
  private fieldHandler: FieldHandler | null = null;

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

    this.fieldHandler = this.createFieldHandler();
    this.fieldHandler?.setup(signal);
  }

  private createFieldHandler(): FieldHandler | null {
    const onSubmit = () => {
      this.changeHandled = true;
      if (this.form) {
        this.submitForm(this.form);
      }
    };

    const onCancel = () => {
      this.cancelEdit();
    };

    const onValueChange = (changed: boolean) => {
      this.changeHandled = changed;
    };

    if (this.fieldType === 'select' || this.fieldType === 'multi-select') {
      const select = this.form?.querySelector('select');
      if (select instanceof HTMLSelectElement) {
        return new SelectFieldHandler(
          select,
          onSubmit,
          onCancel,
          onValueChange,
        );
      }
    } else if (this.fieldType === 'date') {
      const dateInput = this.form?.querySelector('input[type="date"]');
      if (dateInput instanceof HTMLInputElement) {
        return new DateFieldHandler(
          dateInput,
          onSubmit,
          onCancel,
          onValueChange,
        );
      }
    }

    return null;
  }

  private handleAfterRequest = (): void => {
    this.isSubmitting = false;
    this.changeHandled = false;
  };

  private handleResponseError = (): void => {
    this.isSubmitting = false;
    this.changeHandled = false;
  };

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
