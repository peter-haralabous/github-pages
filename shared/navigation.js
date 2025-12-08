export function initNav(root = null) {
  const mount = root || document.getElementById('site-header') || document.body;
  // Ensure the mount is an element we can populate
  if (!mount) return;
  mount.className = 'global-header';
  // Use the base href from the document, or default to '/'
  const baseHref = document.querySelector('base')?.href || window.location.origin + '/';
  const homePath = baseHref.replace(window.location.origin, '');
  mount.innerHTML = `
    <div class="global-header__inner flex w-full justify-between items-center">
      <a href="${homePath}" class="brand no-underline">
        <span class="logo">HC</span>
        <span class="brand-name">HealthConnect</span>
      </a>
      <div class="search" aria-hidden="true" class="mx-auto">
        <input type="search" placeholder="Type a command or search..." aria-label="Search" />
      </div>
      <div class="actions" style="display:flex;align-items:center;gap:12px">
        <button class="icon-btn" aria-label="Open quick actions" title="Open quick actions">
          <span class="material-symbols-outlined">  </span>
        </button>
        <div class="user" title="JD">JD</div>
      </div>
    </div>
  `;
  if (!document.body.classList.contains('has-global-header')) {
    document.body.classList.add('has-global-header');
  }
}
