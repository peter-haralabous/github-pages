import htmx from 'htmx.org';
import 'htmx-ext-sse';

// Explicitly attach htmx to window so it's available globally
// This is needed because webpack bundles may not expose it automatically
if (typeof window !== 'undefined') {
  (window as any).htmx = htmx;
}
