const menuButton = document.querySelector('.menu-button');
const navigation = document.querySelector('#site-nav');
const grid = document.querySelector('#skill-grid');
const count = document.querySelector('#result-count');
const filterButtons = [...document.querySelectorAll('.filter')];

const skills = [
  { name: 'nostr-cli', desk: 'communicate', label: 'Communication', summary: 'Manage identities, relays, posts, replies, follows, DMs, and long-form publishing on Nostr.' },
  { name: 'signal-cli', desk: 'communicate', label: 'Communication', summary: 'Send private messages and attachments, inspect contacts, and operate group workflows.' },
  { name: 'mdk-agent-wallet', desk: 'transact', label: 'Money', summary: 'Operate self-custodial agent wallets for Lightning balances, payments, history, and L402 access.' },
  { name: 'mdk-l402-api', desk: 'transact', label: 'Money', summary: 'Build paid Next.js or Express APIs using HTTP 402 and Lightning payment flows.' },
  { name: 'mdk-mcp', desk: 'transact', label: 'Money', summary: 'Connect coding agents to Money Dev Kit through the Model Context Protocol.' },
  { name: 'mdk-nextjs-checkout', desk: 'build', label: 'Developer workflow', summary: 'Add a Lightning checkout to Next.js App Router applications.' },
  { name: 'mdk-replit-checkout', desk: 'build', label: 'Developer workflow', summary: 'Add a Lightning checkout to Replit Vite, React, and Express applications.' },
  { name: 'rampart-hook-configurator', desk: 'protect', label: 'Privacy', summary: 'Configure paired Rampart hooks to reduce sensitive-data exposure in agent workflows.' },
  { name: 'skillspector', desk: 'protect', label: 'Safety', summary: 'Scan individual skills or full repositories for security concerns before installation.' },
  { name: 'timelock-sh', desk: 'protect', label: 'Resilience', summary: 'Time-lock, inspect, and decrypt files with timelock.sh.' },
  { name: 'p2p-transfer-filepizza', desk: 'preserve', label: 'Sharing', summary: 'Share local files through temporary peer-to-peer FilePizza links.' },
  { name: 'wayback-archive', desk: 'preserve', label: 'Preservation', summary: 'Archive webpages, check snapshots, and create stable citation links.' },
  { name: 'domain-intel', desk: 'investigate', label: 'Research', summary: 'Conduct passive domain reconnaissance across DNS, WHOIS, certificates, and availability.' },
  { name: 'fast-transcript', desk: 'investigate', label: 'Media', summary: 'Transcribe and inspect audio or video from local files and supported URLs.' },
  { name: 'mo-ux-vibedesign-btc', desk: 'build', label: 'Product', summary: 'Run senior Bitcoin UX reviews across research, copy, flows, wireframes, and benchmarks.' },
];

function renderSkills(filter = 'all') {
  const visible = filter === 'all' ? skills : skills.filter((skill) => skill.desk === filter);
  grid.innerHTML = visible.map((skill, index) => `
    <article class="skill-card" style="--order:${index}">
      <div class="card-meta"><span>${skill.label}</span><span>${String(index + 1).padStart(2, '0')}</span></div>
      <h3>${skill.name}</h3>
      <p>${skill.summary}</p>
      <a href="https://github.com/brenorb/freedom-skills/tree/main/skills/${skill.name}" aria-label="Read the ${skill.name} source">Read the field notes <span aria-hidden="true">↗</span></a>
    </article>
  `).join('');
  count.textContent = visible.length;
}

menuButton.addEventListener('click', () => {
  const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!isOpen));
  navigation.classList.toggle('is-open', !isOpen);
});

navigation.addEventListener('click', (event) => {
  if (event.target.matches('a')) {
    menuButton.setAttribute('aria-expanded', 'false');
    navigation.classList.remove('is-open');
  }
});

filterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    filterButtons.forEach((item) => {
      const active = item === button;
      item.classList.toggle('is-active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    renderSkills(button.dataset.filter);
  });
});

renderSkills();
