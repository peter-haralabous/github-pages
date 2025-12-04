import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { initCustomAttributeEnumFormsets } from './enum-formset';

function createFormsetContainer(
  options: {
    initialFormCount?: number;
    includeDeleteCheckbox?: boolean;
  } = {},
): HTMLElement {
  const { initialFormCount = 1, includeDeleteCheckbox = false } = options;

  const container = document.createElement('div');
  container.setAttribute('data-enum-formset', '');

  const totalFormsInput = document.createElement('input');
  totalFormsInput.type = 'hidden';
  totalFormsInput.name = 'enums-TOTAL_FORMS';
  totalFormsInput.value = String(initialFormCount);
  container.appendChild(totalFormsInput);

  const formsContainer = document.createElement('div');
  formsContainer.id = 'enum-forms';

  for (let i = 0; i < initialFormCount; i++) {
    formsContainer.appendChild(createEnumFormRow(i, includeDeleteCheckbox));
  }

  container.appendChild(formsContainer);

  const addButton = document.createElement('button');
  addButton.id = 'add-option-btn';
  addButton.type = 'button';
  addButton.textContent = 'Add Option';
  container.appendChild(addButton);

  return container;
}

function createEnumFormRow(
  index: number,
  includeDeleteCheckbox: boolean,
): HTMLElement {
  const formRow = document.createElement('div');
  formRow.className = 'enum-form-row';

  const labelInput = document.createElement('input');
  labelInput.type = 'text';
  labelInput.name = `enums-${index}-label`;
  labelInput.value = '';
  formRow.appendChild(labelInput);

  const valueInput = document.createElement('input');
  valueInput.type = 'text';
  valueInput.name = `enums-${index}-value`;
  valueInput.value = '';
  formRow.appendChild(valueInput);

  // DELETE checkbox (for existing forms)
  if (includeDeleteCheckbox) {
    const deleteCheckbox = document.createElement('input');
    deleteCheckbox.type = 'checkbox';
    deleteCheckbox.name = `enums-${index}-DELETE`;
    formRow.appendChild(deleteCheckbox);
  }

  const csrfInput = document.createElement('input');
  csrfInput.type = 'hidden';
  csrfInput.name = 'csrfmiddlewaretoken';
  csrfInput.value = 'test-csrf-token';
  formRow.appendChild(csrfInput);

  const deleteButton = document.createElement('button');
  deleteButton.type = 'button';
  deleteButton.className = 'delete-option-btn';
  deleteButton.textContent = 'Delete';
  formRow.appendChild(deleteButton);

  return formRow;
}

describe('CustomAttributeEnumFormset', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Initialization', () => {
    it('initializes formset when data-enum-formset container exists', () => {
      const container = createFormsetContainer();
      document.body.appendChild(container);

      expect(() => initCustomAttributeEnumFormsets()).not.toThrow();
    });

    it('throws error when required elements are missing', () => {
      const container = document.createElement('div');
      container.setAttribute('data-enum-formset', '');
      document.body.appendChild(container);

      const consoleErrorSpy = vi
        .spyOn(console, 'error')
        .mockImplementation(() => {});
      initCustomAttributeEnumFormsets();

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Failed to initialize custom attribute enum formset:',
        expect.any(Error),
      );
    });

    it('does not re-initialize already initialized formsets', () => {
      const container = createFormsetContainer();
      document.body.appendChild(container);

      initCustomAttributeEnumFormsets();
      const deleteButtons = container.querySelectorAll('.delete-option-btn');

      const addEventListenerSpy = vi.spyOn(
        deleteButtons[0],
        'addEventListener',
      );
      initCustomAttributeEnumFormsets();
      expect(addEventListenerSpy).not.toHaveBeenCalled();
    });
  });

  describe('Adding Forms', () => {
    it('adds a new form when add button is clicked', () => {
      const container = createFormsetContainer({ initialFormCount: 1 });
      document.body.appendChild(container);
      initCustomAttributeEnumFormsets();

      const addButton =
        container.querySelector<HTMLButtonElement>('#add-option-btn')!;
      const formsContainer = container.querySelector('#enum-forms')!;

      expect(formsContainer.querySelectorAll('.enum-form-row')).toHaveLength(1);

      addButton.click();

      expect(formsContainer.querySelectorAll('.enum-form-row')).toHaveLength(2);
    });

    it('increments TOTAL_FORMS when adding a new form', () => {
      const container = createFormsetContainer({ initialFormCount: 2 });
      document.body.appendChild(container);
      initCustomAttributeEnumFormsets();

      const addButton =
        container.querySelector<HTMLButtonElement>('#add-option-btn')!;
      const totalFormsInput = container.querySelector<HTMLInputElement>(
        '[name="enums-TOTAL_FORMS"]',
      )!;

      expect(totalFormsInput.value).toBe('2');

      addButton.click();

      expect(totalFormsInput.value).toBe('3');
    });

    it('updates form indices correctly when adding forms', () => {
      const container = createFormsetContainer({ initialFormCount: 1 });
      document.body.appendChild(container);
      initCustomAttributeEnumFormsets();

      const addButton =
        container.querySelector<HTMLButtonElement>('#add-option-btn')!;
      addButton.click();

      const newForm = container.querySelectorAll('.enum-form-row')[1];
      const labelInput = newForm.querySelector<HTMLInputElement>(
        'input[name="enums-1-label"]',
      );
      const valueInput = newForm.querySelector<HTMLInputElement>(
        'input[name="enums-1-value"]',
      );

      expect(labelInput).toBeTruthy();
      expect(valueInput).toBeTruthy();
    });

    it('clears input values in newly added forms', () => {
      const container = createFormsetContainer({ initialFormCount: 1 });
      document.body.appendChild(container);

      const templateInput = container.querySelector<HTMLInputElement>(
        'input[name="enums-0-label"]',
      )!;
      templateInput.value = 'Template Value';

      initCustomAttributeEnumFormsets();

      const addButton =
        container.querySelector<HTMLButtonElement>('#add-option-btn')!;
      addButton.click();

      const newFormInput = container.querySelector<HTMLInputElement>(
        'input[name="enums-1-label"]',
      )!;
      expect(newFormInput.value).toBe('');
    });

    it('copies CSRF token to newly added forms', () => {
      const container = createFormsetContainer({ initialFormCount: 1 });
      document.body.appendChild(container);
      initCustomAttributeEnumFormsets();

      const addButton =
        container.querySelector<HTMLButtonElement>('#add-option-btn')!;
      addButton.click();

      const newForm = container.querySelectorAll('.enum-form-row')[1];
      const csrfToken = newForm.querySelector<HTMLInputElement>(
        'input[name="csrfmiddlewaretoken"]',
      );

      expect(csrfToken?.value).toBe('test-csrf-token');
    });

    it('attaches delete handler to newly added forms', () => {
      const container = createFormsetContainer({ initialFormCount: 1 });
      document.body.appendChild(container);
      initCustomAttributeEnumFormsets();

      const addButton =
        container.querySelector<HTMLButtonElement>('#add-option-btn')!;
      addButton.click();

      const newForm = container.querySelectorAll('.enum-form-row')[1];
      const deleteButton =
        newForm.querySelector<HTMLButtonElement>('.delete-option-btn')!;

      expect(() => deleteButton.click()).not.toThrow();

      // Form should be removed
      expect(container.querySelectorAll('.enum-form-row')).toHaveLength(1);
    });
  });

  describe('Deleting Forms', () => {
    it('removes form when delete button is clicked (no DELETE checkbox)', () => {
      const container = createFormsetContainer({
        initialFormCount: 2,
        includeDeleteCheckbox: false,
      });
      document.body.appendChild(container);
      initCustomAttributeEnumFormsets();

      const deleteButton =
        container.querySelector<HTMLButtonElement>('.delete-option-btn')!;
      deleteButton.click();

      expect(container.querySelectorAll('.enum-form-row')).toHaveLength(1);
    });

    it('decrements TOTAL_FORMS when deleting a form (no DELETE checkbox)', () => {
      const container = createFormsetContainer({
        initialFormCount: 3,
        includeDeleteCheckbox: false,
      });
      document.body.appendChild(container);
      initCustomAttributeEnumFormsets();

      const totalFormsInput = container.querySelector<HTMLInputElement>(
        '[name="enums-TOTAL_FORMS"]',
      )!;
      expect(totalFormsInput.value).toBe('3');

      const deleteButton =
        container.querySelector<HTMLButtonElement>('.delete-option-btn')!;
      deleteButton.click();

      expect(totalFormsInput.value).toBe('2');
    });

    it('hides form and checks DELETE checkbox when deleting existing form', () => {
      const container = createFormsetContainer({
        initialFormCount: 2,
        includeDeleteCheckbox: true,
      });
      document.body.appendChild(container);
      initCustomAttributeEnumFormsets();

      const formRow = container.querySelector<HTMLElement>('.enum-form-row')!;
      const deleteButton =
        formRow.querySelector<HTMLButtonElement>('.delete-option-btn')!;
      const deleteCheckbox = formRow.querySelector<HTMLInputElement>(
        'input[name$="-DELETE"]',
      )!;

      expect(formRow.style.display).not.toBe('none');
      expect(deleteCheckbox.checked).toBe(false);

      deleteButton.click();

      expect(formRow.style.display).toBe('none');
      expect(deleteCheckbox.checked).toBe(true);
    });

    it('does not decrement TOTAL_FORMS when hiding form with DELETE checkbox', () => {
      const container = createFormsetContainer({
        initialFormCount: 2,
        includeDeleteCheckbox: true,
      });
      document.body.appendChild(container);
      initCustomAttributeEnumFormsets();

      const totalFormsInput = container.querySelector<HTMLInputElement>(
        '[name="enums-TOTAL_FORMS"]',
      )!;
      expect(totalFormsInput.value).toBe('2');

      const deleteButton =
        container.querySelector<HTMLButtonElement>('.delete-option-btn')!;
      deleteButton.click();

      // Should remain 2 because form is hidden, not removed
      expect(totalFormsInput.value).toBe('2');
    });

    it('does not decrement TOTAL_FORMS below 0', () => {
      const container = createFormsetContainer({
        initialFormCount: 1,
        includeDeleteCheckbox: false,
      });
      document.body.appendChild(container);
      initCustomAttributeEnumFormsets();

      const totalFormsInput = container.querySelector<HTMLInputElement>(
        '[name="enums-TOTAL_FORMS"]',
      )!;
      const deleteButton =
        container.querySelector<HTMLButtonElement>('.delete-option-btn')!;

      deleteButton.click();

      expect(totalFormsInput.value).toBe('0');

      expect(parseInt(totalFormsInput.value, 10)).toBeGreaterThanOrEqual(0);
    });
  });
});
