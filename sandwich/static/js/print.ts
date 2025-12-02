/**
 * Print functionality
 * Loads print view into hidden iframe and triggers browser print
 * This is needed to ensure pagination works correctly when printing modals
 */

async function handlePrintClick(this: Element, e: Event) {
  e.preventDefault();

  const button = this as HTMLElement;
  const printUrl = button.dataset.printUrl;

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
  try {
    const response = await fetch(printUrl);
    const html = await response.text();

    const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
    if (!iframeDoc) {
      console.error('Could not access iframe document');
      return;
    }

    iframeDoc.open();
    iframeDoc.write(html);
    iframeDoc.close();

    // Wait for styles to load, then print
    iframe.onload = () => {
      requestAnimationFrame(() => {
        iframe.contentWindow?.focus();
        iframe.contentWindow?.print();
      });
    };
  } catch (error) {
    console.error('Error loading print view:', error);
  }
}

// Setup on page load and after HTMX swaps
// @ts-ignore - htmx is loaded globally
htmx.onLoad(function (content: HTMLElement) {
  const buttons = content.querySelectorAll('.js-print');

  buttons.forEach((button: Element) => {
    button.addEventListener('click', handlePrintClick);
  });
});
