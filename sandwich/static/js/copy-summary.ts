/**
 * Handle copy-to-clipboard functionality for summary content
 */

export function setupCopyButtons() {
  document
    .querySelectorAll<HTMLButtonElement>('.js-copy-summary')
    .forEach((button) => {
      if (button.dataset.copyListenerAttached) return;
      button.dataset.copyListenerAttached = 'true';

      button.addEventListener('click', async () => {
        const textToCopy = button.dataset.copyText;
        if (!textToCopy) return;

        try {
          const originalHTML = button.innerHTML;
          button.disabled = true;
          await navigator.clipboard.writeText(textToCopy);
          button.textContent = 'Copied!';

          setTimeout(() => {
            button.innerHTML = originalHTML;
            button.disabled = false;
          }, 2000);
        } catch (err) {
          console.error('Failed to copy text:', err);
          button.disabled = false;
        }
      });
    });
}

// Setup on page load and after HTMX swaps
document.addEventListener('DOMContentLoaded', () => {
  setupCopyButtons();
  document.body.addEventListener('htmx:afterSwap', setupCopyButtons);
});
