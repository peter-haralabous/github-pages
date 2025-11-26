import { LitElement, html, css, type PropertyValues } from 'lit';
import { customElement, property } from 'lit/decorators.js';

import { Editor } from '@tiptap/core';
import {
  createIcons,
  Undo,
  Redo,
  Heading1,
  Heading2,
  Heading3,
  Heading4,
  Bold,
  Italic,
  Strikethrough,
  Underline as UnderlineIcon,
  Highlighter,
  Quote,
  Link as LinkIcon,
  AlignLeft,
  AlignCenter,
  AlignRight,
  List,
  ListOrdered,
} from 'lucide';

const styles = css`
  wysiwyg-editor-toolbar {
    .btn > svg {
      width: 1rem;
    }
  }
`.styleSheet!;

@customElement('wysiwyg-editor-toolbar')
export class WysiwygEditorToolbar extends LitElement {
  @property({ attribute: false }) accessor editor: Editor | null = null;

  // Render in Light DOM to work with daisy-ui
  protected createRenderRoot() {
    const rootNode = this.getRootNode() as ShadowRoot | Document;
    if (!rootNode.adoptedStyleSheets.includes(styles)) {
      rootNode.adoptedStyleSheets.push(styles);
    }
    return this;
  }

  protected firstUpdated(_changedProperties: PropertyValues): void {
    createIcons({
      icons: {
        Undo,
        Redo,
        Heading1,
        Heading2,
        Heading3,
        Heading4,
        Bold,
        Italic,
        Strikethrough,
        Underline: UnderlineIcon,
        Highlighter,
        Quote,
        Link: LinkIcon,
        List,
        ListOrdered,
        AlignLeft,
        AlignCenter,
        AlignRight,
      },
    });
  }

  protected updated(changedProperties: PropertyValues): void {
    // Set up event listeners when editor becomes available
    if (changedProperties.has('editor') && this.editor) {
      this.editor.on('selectionUpdate', () => this.requestUpdate());
      this.editor.on('update', () => this.requestUpdate());
      this.editor.on('transaction', () => this.requestUpdate());
    }
  }

  private _setLink() {
    if (!this.editor) return;

    const previousUrl = this.editor.getAttributes('link').href;
    const url = window.prompt('Enter URL:', previousUrl);

    if (url === null) return; // Cancelled

    if (url === '') {
      this.editor.chain().focus().extendMarkRange('link').unsetLink().run();
      return;
    }

    this.editor
      .chain()
      .focus()
      .extendMarkRange('link')
      .setLink({ href: url })
      .run();
  }

  render() {
    return html`
      <nav class="overflow-auto max-w-full">
        <ul class="flex bg-base-100">
          <!-- Undo/Redo -->
          <li class="menu-disabled">
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button"
              @click=${() => this.editor?.chain().focus().undo().run()}
              ?disabled=${!this.editor || !this.editor.can().undo()}
              title="Undo"
            >
              <i data-lucide="undo"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button"
              @click=${() => this.editor?.chain().focus().redo().run()}
              ?disabled=${!this.editor || !this.editor.can().redo()}
              title="Redo"
            >
              <i data-lucide="redo"></i>
            </button>
          </li>
          <div class="divider divider-horizontal"></div>

          <!-- Headings -->
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'heading',
                {
                  level: 1,
                },
              )
                ? 'btn-primary'
                : ''}"
              @click=${() =>
                this.editor?.chain().focus().toggleHeading({ level: 1 }).run()}
              ?disabled=${!this.editor}
              title="Heading 1"
            >
              <i data-lucide="heading-1"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'heading',
                {
                  level: 2,
                },
              )
                ? 'btn-primary'
                : ''}"
              @click=${() =>
                this.editor?.chain().focus().toggleHeading({ level: 2 }).run()}
              ?disabled=${!this.editor}
              title="Heading 2"
            >
              <i data-lucide="heading-2"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'heading',
                {
                  level: 3,
                },
              )
                ? 'btn-primary'
                : ''}"
              @click=${() =>
                this.editor?.chain().focus().toggleHeading({ level: 3 }).run()}
              ?disabled=${!this.editor}
              title="Heading 3"
            >
              <i data-lucide="heading-3"></i>
            </button>
          </li>
          <div class="divider divider-horizontal"></div>

          <!-- Text Styling -->
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'bold',
              )
                ? 'btn-primary'
                : ''}"
              @click=${() => this.editor?.chain().focus().toggleBold().run()}
              ?disabled=${!this.editor}
              title="Bold"
            >
              <i data-lucide="bold"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'italic',
              )
                ? 'btn-primary'
                : ''}"
              @click=${() => this.editor?.chain().focus().toggleItalic().run()}
              ?disabled=${!this.editor}
              title="Italic"
            >
              <i data-lucide="italic"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'strike',
              )
                ? 'btn-primary'
                : ''}"
              @click=${() => this.editor?.chain().focus().toggleStrike().run()}
              ?disabled=${!this.editor}
              title="Strikethrough"
            >
              <i data-lucide="strikethrough"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'underline',
              )
                ? 'btn-primary'
                : ''}"
              @click=${() =>
                this.editor?.chain().focus().toggleUnderline().run()}
              ?disabled=${!this.editor}
              title="Underline"
            >
              <i data-lucide="underline"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'highlight',
              )
                ? 'btn-primary'
                : ''}"
              @click=${() =>
                this.editor?.chain().focus().toggleHighlight().run()}
              ?disabled=${!this.editor}
              title="Highlight"
            >
              <i data-lucide="highlighter"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'blockquote',
              )
                ? 'btn-primary'
                : ''}"
              @click=${() =>
                this.editor?.chain().focus().toggleBlockquote().run()}
              ?disabled=${!this.editor}
              title="Blockquote"
            >
              <i data-lucide="quote"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'link',
              )
                ? 'btn-primary'
                : ''}"
              @click=${() => this._setLink()}
              ?disabled=${!this.editor}
              title="Link"
            >
              <i data-lucide="link"></i>
            </button>
          </li>
          <div class="divider divider-horizontal"></div>

          <!-- Lists -->
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'bulletList',
              )
                ? 'btn-primary'
                : ''}"
              @click=${() =>
                this.editor?.chain().focus().toggleBulletList().run()}
              ?disabled=${!this.editor}
              title="Bullet List"
            >
              <i data-lucide="list"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                'orderedList',
              )
                ? 'btn-primary'
                : ''}"
              @click=${() =>
                this.editor?.chain().focus().toggleOrderedList().run()}
              ?disabled=${!this.editor}
              title="Numbered List"
            >
              <i data-lucide="list-ordered"></i>
            </button>
          </li>
          <div class="divider divider-horizontal"></div>

          <!-- Text Align -->
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                {
                  textAlign: 'left',
                },
              )
                ? 'btn-primary'
                : ''}"
              @click=${() =>
                this.editor?.chain().focus().setTextAlign('left').run()}
              ?disabled=${!this.editor}
              title="Align Left"
            >
              <i data-lucide="align-left"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                {
                  textAlign: 'center',
                },
              )
                ? 'btn-primary'
                : ''}"
              @click=${() =>
                this.editor?.chain().focus().setTextAlign('center').run()}
              ?disabled=${!this.editor}
              title="Align Center"
            >
              <i data-lucide="align-center"></i>
            </button>
          </li>
          <li>
            <button
              type="button"
              class="btn btn-ghost btn-xs join-item toolbar-button ${this.editor?.isActive(
                {
                  textAlign: 'right',
                },
              )
                ? 'btn-primary'
                : ''}"
              @click=${() =>
                this.editor?.chain().focus().setTextAlign('right').run()}
              ?disabled=${!this.editor}
              title="Align Right"
            >
              <i data-lucide="align-right"></i>
            </button>
          </li>
        </ul>
      </nav>
    `;
  }
}
