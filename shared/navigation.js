export function initNav(root = document.body){
  const nav = document.createElement('nav');
  nav.className = 'site-nav container';
  nav.innerHTML = `
    <a class="brand" href="/">Prototypes</a>
    <div style="flex:1"></div>
    <a href="/patient-details/">Patient</a>
    <a href="/scheduling/">Scheduling</a>
    <a href="/dashboard/">Dashboard</a>
  `;
  root.innerHTML = '';
  root.appendChild(nav);
}
