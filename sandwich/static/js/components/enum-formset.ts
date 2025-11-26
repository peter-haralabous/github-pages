/**
 * Custom Attribute Enum Formset Manager
 * Handles dynamic add/delete of enum option forms in a Django formset
 */

interface FormsetElements {
  container: HTMLElement;
  formsContainer: HTMLElement;
  addButton: HTMLButtonElement;
  totalFormsInput: HTMLInputElement;
}

class EnumFormset {
  private readonly elements: FormsetElements;
  private deleteHandlers = new Map<HTMLElement, AbortController>();

  constructor(container: HTMLElement) {
    const formsContainer = container.querySelector<HTMLElement>('#enum-forms');
    const addButton =
      container.querySelector<HTMLButtonElement>('#add-option-btn');
    const totalFormsInput = container.querySelector<HTMLInputElement>(
      '[name="enums-TOTAL_FORMS"]',
    );

    if (!formsContainer || !addButton || !totalFormsInput) {
      throw new Error('Required formset elements not found');
    }

    this.elements = {
      container,
      formsContainer,
      addButton,
      totalFormsInput,
    };

    this.init();
  }

  private init(): void {
    this.attachDeleteHandlers();
    this.elements.addButton.addEventListener('click', () => this.addNewForm());
  }

  private attachDeleteHandlers(): void {
    const deleteButtons =
      this.elements.formsContainer.querySelectorAll<HTMLButtonElement>(
        '.delete-option-btn',
      );

    deleteButtons.forEach((button) => {
      const formRow = button.closest<HTMLElement>('.enum-form-row');
      if (!formRow || this.deleteHandlers.has(formRow)) {
        return;
      }

      const controller = new AbortController();
      this.deleteHandlers.set(formRow, controller);

      button.addEventListener('click', () => this.handleDelete(formRow), {
        signal: controller.signal,
      });
    });
  }

  private handleDelete(formRow: HTMLElement): void {
    const deleteCheckbox = formRow.querySelector<HTMLInputElement>(
      'input[name$="-DELETE"]',
    );

    if (deleteCheckbox) {
      deleteCheckbox.checked = true;
      formRow.style.display = 'none';
    } else {
      formRow.remove();
      this.decrementTotalForms();
    }

    const controller = this.deleteHandlers.get(formRow);
    if (controller) {
      controller.abort();
      this.deleteHandlers.delete(formRow);
    }
  }

  private addNewForm(): void {
    const templateForm =
      this.elements.formsContainer.querySelector<HTMLElement>('.enum-form-row');
    if (!templateForm) {
      console.error('No template form found');
      return;
    }

    const formCount = this.getCurrentFormCount();
    const newForm = this.cloneAndUpdateForm(templateForm, formCount);

    newForm.style.display = '';
    this.elements.formsContainer.appendChild(newForm);

    this.incrementTotalForms();

    this.attachDeleteHandlers();
  }

  private cloneAndUpdateForm(
    templateForm: HTMLElement,
    formIndex: number,
  ): HTMLElement {
    const newForm = templateForm.cloneNode(true) as HTMLElement;

    this.updateFormIndices(newForm, formIndex);

    // In case we're copying a hidden "deleted" form
    newForm.classList.remove('hidden');
    newForm
      .querySelectorAll<HTMLInputElement>('input[type="text"]')
      .forEach((input) => {
        input.value = '';
      });

    const deleteCheckbox = newForm.querySelector<HTMLInputElement>(
      'input[name$="-DELETE"]',
    );
    if (deleteCheckbox) {
      deleteCheckbox.checked = false;
    }

    this.copyCsrfToken(templateForm, newForm);

    return newForm;
  }

  private updateFormIndices(form: HTMLElement, newIndex: number): void {
    // Update all elements with name, id, or for attributes that contain form indices
    const attributesToUpdate = ['name', 'id', 'for'] as const;
    const selector = attributesToUpdate.map((attr) => `[${attr}]`).join(',');

    form.querySelectorAll<HTMLElement>(selector).forEach((element) => {
      attributesToUpdate.forEach((attr) => {
        const value = element.getAttribute(attr);
        if (value) {
          element.setAttribute(
            attr,
            value.replace(/enums-\d+-/g, `enums-${newIndex}-`),
          );
        }
      });
    });
  }

  private copyCsrfToken(source: HTMLElement, target: HTMLElement): void {
    const sourceToken = source.querySelector<HTMLInputElement>(
      'input[name="csrfmiddlewaretoken"]',
    );
    const targetToken = target.querySelector<HTMLInputElement>(
      'input[name="csrfmiddlewaretoken"]',
    );

    if (sourceToken?.value && targetToken) {
      targetToken.value = sourceToken.value;
    }
  }

  private getCurrentFormCount(): number {
    return parseInt(this.elements.totalFormsInput.value, 10);
  }

  private incrementTotalForms(): void {
    const current = this.getCurrentFormCount();
    this.elements.totalFormsInput.value = String(current + 1);
  }

  private decrementTotalForms(): void {
    const current = this.getCurrentFormCount();
    this.elements.totalFormsInput.value = String(Math.max(0, current - 1));
  }

  destroy(): void {
    this.deleteHandlers.forEach((controller) => controller.abort());
    this.deleteHandlers.clear();
  }
}

const initializedFormsets = new WeakSet<HTMLElement>();

export function initCustomAttributeEnumFormsets(): void {
  document
    .querySelectorAll<HTMLElement>('[data-enum-formset]')
    .forEach((container) => {
      if (initializedFormsets.has(container)) {
        return;
      }

      try {
        new EnumFormset(container);
        initializedFormsets.add(container);
      } catch (error) {
        console.error(
          'Failed to initialize custom attribute enum formset:',
          error,
        );
      }
    });
}

document.addEventListener('data-enum-formset:init', () => {
  initCustomAttributeEnumFormsets();
});
