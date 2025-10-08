## Content Security Policy (CSP)

This document explains our CSP configuration, why it exists, and the rules you must follow when adding HTML, JavaScript,
or styles.

### Goals

- Prevent XSS and data exfiltration.
- Ensure every script & style asset is reviewed and built through our toolchain (webpack + TypeScript + Tailwind).
- Provide strong auditability (nonces + hashing) while still allowing minimal, explicit inline code when truly needed.
- Supply violation reports to monitoring so we can tighten over time.

### Where It Is Configured

Core settings live in Django settings (see `config/settings/`). Look for constants named like `CONTENT_SECURITY_POLICY`,
`CONTENT_SECURITY_POLICY_REPORT_ONLY`, and CSP nonce helpers used by webpack integration.

Webpack loader is configured to inject a nonce on emitted `<script>` / `<style>` tags so they satisfy `script-src` /
`style-src` without `'unsafe-inline'`.

### Key (Enforced) Directives (Snapshot)

(Always confirm in code; this is descriptive, not authoritative.)

- `default-src 'self'`
- `frame-ancestors 'self'`
- `form-action 'self'`
- `img-src 'self' data:`
- `style-src-elem` allows: nonces + explicit hashes for deterministic framework styles (including specific approved
  hashes and `unsafe-hashes` purely to enable hashed inline style allowances)
- `script-src` is intentionally minimal (falls back to `default-src 'self'` + nonce mechanism)

Intentionally absent / not relaxed:

- No broad `'unsafe-inline'` or `'unsafe-eval'`
- No permissive external CDNs by default
- No allowances for inline event attributes (`script-src-attr` remains implicitly restricted)

### Why We Do NOT Allow Ad‑Hoc `<script>` Tags or Inline Event Handlers

Modern CSP Level 3 separates concerns:

- `script-src-elem` governs classic `<script>` elements (inline or external)
- `script-src-attr` governs inline event handler attributes (`onclick=`, `onload=`, etc.) and `javascript:` URLs

We avoid enabling these explicitly because:

1. XSS Surface: Inline event handlers are a high‑risk injection vector.
2. Supply Chain Discipline: All scripts must pass through TypeScript + bundler (lint, type check, tree‑shake, license
   review).
3. Auditability: Nonce or hashed blocks are scarce & reviewable; random in‑template `<script>` tags are not.
4. Gradual Hardening: Keeping policies strict now lets us later add an explicit `script-src` with only `'self'` +
   `nonce-...` without migration pain.

Practically this means:

- Do NOT add `<script src="...">` manually in Django templates for bundled application code. Use
  `{% render_bundle 'vendors' 'js' %}` /
  `{% render_bundle 'project' 'js' %}` or a dedicated bundle you explicitly add (see "Size-Based JavaScript Guidance"
  below). (core bundles are loaded in `base.html`)
- Do NOT add inline event attributes (`onclick=`, `onchange=`, etc.). Attach listeners in module code or inside a Web
  Component.
- Avoid large or complex inline `<script>` blocks. Small, reviewable, **nonced** inline snippets are permitted for truly
  trivial behavior (see criteria below).

#### When a Small Nonced Inline Script Is Acceptable

A tiny inline script *may* be used instead of editing the main bundle **only if ALL of these are true**:

- ≤ ~20 lines (rough heuristic) and no external network requests.
- Purely one-off glue / progressive enhancement not expected to grow.
- No dynamic string construction of HTML via `innerHTML` / `document.write`.
- Uses `nonce="{{ request.csp_nonce }}"` (Django context) and optionally `type="module"` if ES module syntax is needed.
- Contains no user-supplied interpolated data except via safely escaped template context.

If it violates any criterion, move it to `project.ts` (medium) or a new entrypoint (large).

```
<script nonce="{{ request.csp_nonce }}">
  // tiny enhancement only
  document.addEventListener('DOMContentLoaded', () => {
    const el = document.querySelector('[data-dismiss]');
    if (el) el.addEventListener('click', () => el.remove());
  });
</script>
```

### Size-Based JavaScript Guidance (Bridging CSP & Bundling)

Pick the lightest compliant option:

1. Small (inline, nonced): Trivial, self-limiting snippet (criteria above). Avoid imports; keep future growth unlikely.
2. Medium (add to existing bundle): Add code to `sandwich/static/js/project.ts` (or imported modules it pulls in) when
   functionality is moderate, shared, or likely to evolve.
3. Large (new entrypoint): Create a new file (e.g. `sandwich/static/js/reports.ts`) and register a webpack entry so it
   builds into its own bundle you can include with `{% render_bundle 'reports' 'js' %}`. This keeps initial payload lean
   and isolates rarely used features.

Adding a new entrypoint:

- Create the file under `sandwich/static/js/<name>.ts`.
- Edit `webpack/common.config.cjs` `entry` object, e.g. add:
  ```js
  entry: {
    project: path.resolve(__dirname, '../sandwich/static/js/project'),
    vendors: path.resolve(__dirname, '../sandwich/static/js/vendors'),
    reports: path.resolve(__dirname, '../sandwich/static/js/reports'), // new
  }
  ```
- Rebuild (`npm run build` or dev server) so `webpack-stats.json` updates.
- In the template that needs it: `{% render_bundle 'reports' 'js' %}` (only on pages that require it).

Rationale: This tiered approach balances CSP strictness with pragmatic development velocity.

### Nonces vs Hashes

- Nonces: Rotated per response, allow controlled inline bootstrap snippets without committing to a hash in settings.
- Hashes: Used for deterministic inline style blocks (e.g. libraries that inject a stable `<style>` tag) so we can still
  forbid `'unsafe-inline'`.
- We strive to eliminate the need for either for scripts (ideal state: all code external + nonce, zero inline JS).

### Adding JavaScript Safely

1. For small trivial behavior, prefer a tiny inline nonced snippet (criteria above). Otherwise:
2. Author code in `sandwich/static/js/**` (TypeScript preferred).
3. For moderate features, extend `project.ts` or import new modules from it.
4. For large / infrequently used features, add a new entrypoint (see earlier) and lazy-load via template inclusion.
5. Register Web Components (Lit) or add module initialization under `DOMContentLoaded`.
6. Rebuild; emitted bundles automatically receive CSP nonces through the loader integration.

### Absolutely Avoid

- Inline event attributes (`onclick=`, `oninput=`, etc.).
- Manually inserted `<script src>` tags (with or without `src`) for application code bypassing bundling.
- Third‑party CDN script includes added outside the bundler (unless an explicit reviewed exception is granted).
- Adding `'unsafe-inline'` or `'unsafe-eval'` to directives.

### Quick Reference

Allowed:

- Bundled scripts via `{% render_bundle %}` (auto nonce)
- Small, reviewable nonced inline bootstrap/enhancement snippets (see criteria)
- Web Component custom elements
- New dedicated bundles for large features (add new webpack entry + `{% render_bundle %}`)

Disallowed:

- Inline event attributes
- Handwritten `<script src>` in templates that bypass webpack
- Large or complex inline `<script>` blocks (should be bundled)

> [!NOTE]
> Unsure if something fits? Default to the strict path: bundle it or build a Web Component. Ask in code review before
> introducing anything borderline; small inline scripts must stay tiny & nonced.
