const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#primary-nav');

menuButton?.addEventListener('click', () => {
  const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!isOpen));
  navigation.dataset.open = String(!isOpen);
});

navigation?.addEventListener('click', (event) => {
  if (event.target.closest('a')) {
    menuButton?.setAttribute('aria-expanded', 'false');
    navigation.dataset.open = 'false';
  }
});

const filters = [...document.querySelectorAll('.filter')];
const cards = [...document.querySelectorAll('.skill-card')];
const filterStatus = document.querySelector('.filter-status');

filters.forEach((filter) => {
  filter.addEventListener('click', () => {
    const selected = filter.dataset.filter;
    let visible = 0;

    filters.forEach((item) => {
      const active = item === filter;
      item.classList.toggle('is-active', active);
      item.setAttribute('aria-pressed', String(active));
    });

    cards.forEach((card) => {
      const matches = selected === 'all' || card.dataset.category === selected;
      card.hidden = !matches;
      if (matches) visible += 1;
    });

    if (filterStatus) {
      const label = filter.textContent.replace(/\s*\/.*$/, '').trim().toLowerCase();
      filterStatus.textContent = selected === 'all'
        ? `Showing all ${visible} field kits.`
        : `Showing ${visible} ${label} field kit${visible === 1 ? '' : 's'}.`;
    }
  });
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && navigation?.dataset.open === 'true') {
    menuButton.setAttribute('aria-expanded', 'false');
    navigation.dataset.open = 'false';
    menuButton.focus();
  }
});
