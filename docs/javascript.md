## JavaScript & Web Components Strategy

We use modern, modular JavaScript with a preference for **Web Components built using [Lit](https://lit.dev)**. This
document outlines when to write a component, where files live, and what to avoid.

### Principles

- Encapsulation: UI behavior + template + styles should live together (Web Component) instead of scattered DOM hooks.
- Declarative usage: Templates instantiate components via custom tags (`<command-palette>`, `<message-alert>`), reducing
  imperative glue code.
- Type safety: Prefer TypeScript for all new code. Decorators (`@property`) and `accessor` syntax are supported (see
  `tsconfig.json` enabling `experimentalDecorators`).
- Minimal global scripts: Avoid large, monolithic entry files manipulating arbitrary selectors.
- Tiered delivery: Choose the smallest compliant delivery mechanism (see Size-Based Guidance) to keep bundles lean and
  CSP tight.

### Size-Based Guidance (Choosing How to Ship Code)

Pick one of three sizes. Start lower; move up if the feature grows.

1. Small (inline, nonced snippet)
    - Use ONLY for trivial, self-contained enhancement (≤ ~20 lines, no fetch/XHR, no dynamic HTML string building).
    - Must include `nonce="{{ request.csp_nonce }}"`.
    - Optional `type="module"` if you need modern syntax (no imports from local files—keep it self-contained).
    - If it grows beyond trivial, migrate to Medium.
      Example:
   ```html
   <script nonce="{{ request.csp_nonce }}">
     document.addEventListener('DOMContentLoaded', () => {
       const btn = document.querySelector('[data-dismiss]');
       if (btn) btn.addEventListener('click', () => btn.remove());
     });
   </script>
   ```

2. Medium (add to existing `project.ts` bundle)
    - Default for most new features.
    - Create a module under `sandwich/static/js/<feature>.ts` and import it from `project.ts` OR directly add logic
      there.
    - Suitable when: code may evolve, reused across pages, or more than a handful of lines.

3. Large (new dedicated entrypoint)
    - For substantial or infrequently used areas (e.g., analytics dashboard, large admin tool) where isolating payload
      improves performance.
    - Steps:
        1. Create `sandwich/static/js/<name>.ts`.
        2. Add an entry in `webpack/common.config.cjs`:
           ```js
           entry: {
             project: path.resolve(__dirname, '../sandwich/static/js/project'),
             vendors: path.resolve(__dirname, '../sandwich/static/js/vendors'),
             <name>: path.resolve(__dirname, `../sandwich/static/js/<name>`),
           }
           ```
        3. Rebuild (dev server auto or `npm run build`).
        4. Include only on needed template(s): `{% render_bundle '<name>' 'js' %}`.

Decision flow:

- Is it truly trivial, one-off, and unlikely to grow? Small.
- Will it share code, grow, or benefit from TypeScript/imports? Medium.
- Is it large or rarely needed so we should avoid inflating baseline? Large.

### Directory Layout

Source JS/TS lives under:

- `sandwich/static/js/` – author your modules & components here.
- `sandwich/static/js/components/` – Lit components (e.g. `command-palette.ts`, `message.ts`).

Built assets are output by webpack; the template includes them via:

- `{% render_bundle 'vendors' 'js' %}` – third‑party vendor bundle.
- `{% render_bundle 'project' 'js' %}` – your application bundle.

Do **not** import from the `staticfiles/` directory; that is a build artifact, excluded from type checking.

### Creating a New Component (Example)

1. Create `sandwich/static/js/components/my-widget.ts`:
    - Define a class extending `LitElement`.
    - Decorate reactive fields with `@property(...) accessor ...`.
    - Register with `@customElement('my-widget')`.
2. Add `<my-widget ...></my-widget>` to a Django template.
3. Rebuild / run dev server; the component upgrades automatically when parsed.

### Example Pattern (`message-alert`)

Template (`partials/messages.html`):

```
<message-alert tags="{{ message.tags }}" message="{{ message }}"></message-alert>
```

Component (`message.ts`):

```
@customElement('message-alert')
export class Message extends LitElement {
  @property({ type: String, attribute: 'tags' }) accessor tags = '';
  @property({ type: String, attribute: 'message' }) accessor message = '';
  ...
}
```

All logic (close button, rendering, styling) stays self‑contained.

### When NOT to Build a Component

Use a lightweight module instead if:

- The behavior is purely progressive enhancement on an existing form or single element.
- There is no reusable UI abstraction and it’s a one‑off (though reconsider if it might repeat).

In that case create `sandwich/static/js/<feature>.ts` and run code on `DOMContentLoaded`:

```
document.addEventListener('DOMContentLoaded', () => {
  const el = document.querySelector('[data-enhance="x"]');
  if (!el) return;
  // enhance
});
```

If logic grows, refactor into a component.

(Add: If the behavior is extremely small and truly one-off, consider a Small inline nonced script instead of even a
module—but migrate if it expands.)

### Avoid Imperative DOM Scanning

Anti‑pattern:

```
// massive init.js
document.querySelectorAll('.some-class').forEach(...)
```

Prefer declarative components that own their subtree. This improves maintainability, testability, and CSP compliance (no
inline handlers).

### TypeScript Conventions

- Always use explicit property types and initialize fields.
- Use `accessor` + `@property` for reactive fields (Lit 3). This ensures getters/setters integrate with Lit's update
  cycle.
- Do not place compiled JS in source directories. Let webpack handle transpilation + bundling.
- Keep `isolatedModules` safety by avoiding global type augmentations unless necessary.

### Interaction With Django

- Templates supply data to components via attributes (strings). For structured data, JSON‑encode into a
  `<script type="application/json" id="...">` tag (nonce applied) and let the component parse it.
- Avoid server‑rendered inline event handlers; components listen for events in their shadow or light DOM.

### Accessing Server Context

Use the JSON script tags in `base.html` (e.g. `environment`, `app_version`) by reading their `textContent` and parsing
as needed. These tags are nonced and CSP‑compliant.

### Testing & Reliability

- Keep rendered DOM minimal in `render()`; heavy logic goes into methods.
- Use dev tools or story-like pages to manually exercise components.
- Future: We can introduce Web Test Runner / Playwright for component tests.

### Performance Tips

- Defer expensive async operations until `updated()` detects the component is connected & visible.
- Cache network responses when appropriate (e.g., search suggestions) to reduce chatter.

### Migration Guidance

If you encounter legacy code that:

- Adds inline `<script>` tags, OR
- Relies on `onclick=` style handlers,
  convert it into a component or a module that attaches listeners programmatically. Remove the inline code from
  templates.

### Third‑Party Libraries

Add them via `import` statements so they land in the vendor bundle. Do **not** add `<script src>` tags directly (
violates our CSP guidance).

### Summary Rules

- Default: Use a Lit Web Component for reusable UI.
- Small enhancement: MAY use a tiny inline nonced `<script>` if it meets the CSP small criteria.
- Medium feature: Add/import code into `project.ts`.
- Large / isolated feature: New webpack entrypoint + `{% render_bundle %}`.
- Never inline event handler attributes.
- Never add raw `<script src>` tags that bypass bundling.
- Move code up the size ladder (small → medium → large) as complexity grows; never let inline snippets accrete
  complexity.

> [!NOTE]
> Unsure? If it might grow, skip the inline snippet and go straight to Medium (bundle) for better maintainability.
