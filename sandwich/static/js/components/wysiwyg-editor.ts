import { LitElement, html, css, type PropertyValues } from 'lit';
import { customElement, property, query, state } from 'lit/decorators.js';

import { Editor } from '@tiptap/core';
import { Placeholder } from '@tiptap/extension-placeholder';
import { Markdown } from '@tiptap/markdown';
import { Underline } from '@tiptap/extension-underline';
import { TextAlign } from '@tiptap/extension-text-align';
import { Link } from '@tiptap/extension-link';
import { Highlight } from '@tiptap/extension-highlight';
import StarterKit from '@tiptap/starter-kit';

const styles = css`
  .tiptap {
    outline: none;
    min-height: 300px;

    /* Placeholder */
    .is-editor-empty:first-child::before {
      color: hsl(var(--bc) / 0.4);
      content: attr(data-placeholder);
      float: left;
      height: 0;
      pointer-events: none;
    }

    p {
      margin: 0.5em 0;
    }

    ul,
    ol {
      padding-left: 1.5rem;
      margin: 0.5em 0;
    }
    ul li {
      list-style-type: disc;
    }
    ol li {
      list-style-type: decimal;
    }
  }
`.styleSheet!;

@customElement('wysiwyg-editor')
export class WysiwygEditor extends LitElement {
  @property({ type: String }) accessor name = '';
  @property({ type: String }) accessor value = '';
  @property({ type: String }) accessor placeholder = '';

  @state() accessor _content = '';
  @state() accessor _editor: Editor | null = null;

  @query('.editor')
  accessor _container!: HTMLDivElement;

  attributeChangedCallback(
    name: string,
    _old: string | null,
    value: string | null,
  ): void {
    super.attributeChangedCallback(name, _old, value);
    if (name === 'value') {
      this._content = value ?? '';
    }
  }

  // Render in Light DOM to work with daisy-ui
  protected createRenderRoot() {
    const rootNode = this.getRootNode() as ShadowRoot | Document;
    if (!rootNode.adoptedStyleSheets.includes(styles)) {
      rootNode.adoptedStyleSheets.push(styles);
    }
    return this;
  }

  protected firstUpdated(_changedProperties: PropertyValues): void {
    this._editor = new Editor({
      element: this._container,
      content: this.value,
      contentType: 'markdown',
      extensions: [
        Markdown,
        StarterKit,
        Placeholder.configure({ placeholder: this.placeholder }),
        Underline,
        Highlight,
        TextAlign.configure({
          types: ['heading', 'paragraph'],
        }),
        Link.configure({
          openOnClick: false,
          HTMLAttributes: {
            class: 'link',
          },
        }),
      ],
      onUpdate: ({ editor }) => {
        this._content = editor.getMarkdown();
      },
    });
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this._editor?.destroy();
  }

  render() {
    return html`<div
      class="textarea textarea-bordered w-full font-mono text-sm min-h-[500px]"
    >
      <wysiwyg-editor-toolbar
        .editor=${this._editor}
        if=${this._editor}
      ></wysiwyg-editor-toolbar>
      <div class="editor p-1"></div>
      <input name="${this.name}" type="hidden" .value=${this._content} />
    </div> `;
  }
}
