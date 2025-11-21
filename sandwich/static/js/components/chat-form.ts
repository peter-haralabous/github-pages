// Chat form component that handles keyboard shortcuts for message submission

document.addEventListener('DOMContentLoaded', () => {
  setupChatFormKeyboardShortcuts();
});

// Re-setup on htmx swaps (when form is replaced)
document.addEventListener('htmx:afterSwap', (event) => {
  const target = (event as any).detail.target;
  if (target?.id === 'chat-form') {
    setupChatFormKeyboardShortcuts();
  }
});

function setupChatFormKeyboardShortcuts() {
  const chatForm = document.getElementById('chat-form');
  if (!chatForm) return;

  const textarea = chatForm.querySelector(
    'textarea[name="message"]',
  ) as HTMLTextAreaElement;
  const submitButton = chatForm.querySelector(
    'button[type="submit"]',
  ) as HTMLButtonElement;

  if (!textarea || !submitButton) return;

  textarea.addEventListener('keydown', (event: Event) => {
    const keyEvent = event as KeyboardEvent;
    // Check for Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux)
    if ((keyEvent.metaKey || keyEvent.ctrlKey) && keyEvent.key === 'Enter') {
      event.preventDefault();
      submitButton.click();
    }
  });
}
