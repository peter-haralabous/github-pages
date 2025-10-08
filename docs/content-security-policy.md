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
- `style-src-elem` allows: nonces + explicit hashes for deterministic framework styles
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

- Do NOT add `<script src="...">` manually in Django templates. Use `{% render_bundle 'vendors' 'js' %}` /
  `{% render_bundle 'project' 'js' %}`. (these are already loaded in `base.html`)
- Do NOT add inline event attributes (`onclick=`, `onchange=`, etc.). Attach listeners in module code or inside a Web
  Component.
- Avoid arbitrary inline `<script>` blocks. If unavoidable, they must have a server‑supplied nonce and be very small
  bootstrap code.

### Nonces vs Hashes

- Nonces: Rotated per response, allow controlled inline bootstrap snippets without committing to a hash in settings.
- Hashes: Used for deterministic inline style blocks (e.g. libraries that inject a stable `<style>` tag) so we can still
  forbid `'unsafe-inline'`.
- We strive to eliminate the need for either for scripts (ideal state: all code external + nonce, zero inline JS).

### Adding JavaScript Safely

1. Author code in `sandwich/static/js/**` (TypeScript preferred).
2. Register Web Components (Lit) or add module initialization under `DOMContentLoaded`.
3. Reference components declaratively in templates via custom tags.
4. Rebuild; emitted bundles automatically receive CSP nonces through the loader integration.

### Absolutely Avoid

- Inline event attributes (`onclick=`, `oninput=`, etc.).
- Manually inserted `<script>` tags (with or without `src`).
- Third‑party CDN script includes added outside the bundler.
- Adding `'unsafe-inline'` or `'unsafe-eval'` to directives.

### If You Think You Need an Exception

Open a PR that includes:

- Justification why bundling is infeasible.
- Proposed minimal inline script.
- Security review notes & impact analysis.
  Expect high scrutiny. Exceptions are deliberately hard.

### Monitoring & Reporting

CSP violation reports are sent to our configured endpoint (see `report_uri` in settings). Dashboards surface:

- Attempts to use inline handlers
- Unexpected external host references
- Deprecated patterns persisting in legacy templates

Use these signals to drive refactors and to remove temporary allowances.

### Future Tightening Roadmap

- Explicit `script-src` with only `'self'` + `nonce-*` once all legacy inline patterns gone.
- Remove any transitional hashes once underlying libraries move to external assets.
- Add Subresource Integrity (SRI) if we ever approve external scripts (currently none).

### Quick Reference

Allowed:

- Bundled scripts via `{% render_bundle %}` (auto nonce)
- Minimal, reviewed nonced inline bootstrap (rare)
- Web Component custom elements

Disallowed:

- Inline event attributes
- Handwritten `<script src>` in templates
- Arbitrary inline `<script>` blocks

> [!NOTE]
> Unsure if something fits? Default to the strict path: bundle it or build a Web Component. Ask in code review before
> introducing any inline script.

