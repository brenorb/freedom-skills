const header = document.querySelector('[data-header]');
const menuButton = document.querySelector('.menu-button');
const navigation = document.querySelector('#site-nav');

if (header && menuButton && navigation) {
  const closeMenu = () => {
    header.classList.remove('menu-open');
    menuButton.setAttribute('aria-expanded', 'false');
  };

  menuButton.addEventListener('click', () => {
    const isOpen = header.classList.toggle('menu-open');
    menuButton.setAttribute('aria-expanded', String(isOpen));
  });

  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMenu();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeMenu();
      menuButton.focus();
    }
  });

  window.addEventListener('resize', () => {
    if (window.matchMedia('(min-width: 761px)').matches) closeMenu();
  });
}

const filterButtons = [...document.querySelectorAll('[data-filter]')];
const skillStrips = [...document.querySelectorAll('[data-category]')];
const filterStatus = document.querySelector('[data-filter-status]');

filterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const selected = button.dataset.filter;

    filterButtons.forEach((candidate) => {
      const isActive = candidate === button;
      candidate.classList.toggle('active', isActive);
      candidate.setAttribute('aria-pressed', String(isActive));
    });

    let visibleCount = 0;
    skillStrips.forEach((strip) => {
      const shouldShow = selected === 'all' || strip.dataset.category === selected;
      strip.hidden = !shouldShow;
      if (shouldShow) visibleCount += 1;
    });

    if (filterStatus) {
      const label = button.textContent.trim().replace(/^All\s+\d+$/i, 'all workbenches');
      filterStatus.textContent = `Showing ${visibleCount} ${visibleCount === 1 ? 'skill' : 'skills'} in ${label}.`;
    }
  });
});
