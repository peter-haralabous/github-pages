import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';

import { WysiwygEditor } from './wysiwyg-editor';

it('should initialize with empty content', async () => {
  const { editor, input } = await createEditorWithContent('');

  expect(editor._content).toBe('');
  expect(input.value).toBe('');
});

it('should initialize with provided markdown content', async () => {
  const markdown = '# Hello World\nThis is a **test**.';

  const { editor, input } = await createEditorWithContent(markdown);

  expect(editor._content).toBe(markdown);
  expect(input.value).toBe(markdown);
});

it('should update hidden input value on editor content change', async () => {
  const initialMarkdown = 'Initial content.';
  const updatedMarkdown = 'Updated content with *italic* text.';

  const { editor, input } = await createEditorWithContent(initialMarkdown);

  // Simulate user updating the content in the editor
  editor._editor?.commands.setContent(updatedMarkdown);
  await editor.updateComplete;

  expect(editor._content).toBe(updatedMarkdown);
  expect(input.value).toBe(updatedMarkdown);
});

async function createEditorWithContent(
  content: string,
  name = 'test_markdown',
) {
  const editor = document.createElement('wysiwyg-editor') as WysiwygEditor;
  editor.setAttribute('name', name);
  editor.setAttribute('value', content);
  document.body.appendChild(editor);

  await editor.updateComplete;

  const input = editor.querySelector(
    `input[name="${name}"]`,
  ) as HTMLInputElement;

  return { editor, input };
}
