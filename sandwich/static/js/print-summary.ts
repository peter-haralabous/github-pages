/**
 * Print summary functionality
 * Loads summary print view into hidden iframe and triggers browser print
 */

function handlePrintClick(this: Element, e: Event) {
  e.preventDefault();

  const button = this as HTMLElement;
  const printUrl = button.dataset.printSummaryUrl;

  if (!printUrl) {
    console.error('Print URL not found on button');
    return;
  }

  // Find or create print iframe
  let iframe = document.getElementById('print-iframe') as HTMLIFrameElement;
  if (!iframe) {
    iframe = document.createElement('iframe');
    iframe.id = 'print-iframe';
    iframe.className = 'hidden';
    document.body.appendChild(iframe);
  }

  // Load print view into iframe
  fetch(printUrl)
    .then((response) => response.text())
    .then((html) => {
      const iframeDoc =
        iframe.contentDocument || iframe.contentWindow?.document;
      if (!iframeDoc) {
        console.error('Could not access iframe document');
        return;
      }

      iframeDoc.open();
      iframeDoc.write(html);
      iframeDoc.close();

      // Wait for styles to load, then print
      setTimeout(() => {
        iframe.contentWindow?.focus();
        iframe.contentWindow?.print();
      }, 500);
    })
    .catch((error) => {
      console.error('Error loading print view:', error);
    });
}

// Attach event listeners to all print buttons
function setupPrintButtons() {
  const buttons = document.querySelectorAll('.js-print-summary');
  buttons.forEach((button) => {
    button.removeEventListener('click', handlePrintClick);
    button.addEventListener('click', handlePrintClick);
  });
}

// Setup on page load and after HTMX swaps
document.addEventListener('DOMContentLoaded', () => {
  setupPrintButtons();
  document.body.addEventListener('htmx:afterSwap', setupPrintButtons);
});
