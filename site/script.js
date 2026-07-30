(() => {
  'use strict';

  const filters = [...document.querySelectorAll('.route-filter')];
  const regions = [...document.querySelectorAll('.route-region')];
  const status = document.querySelector('#filter-status');
  const validRoutes = new Set(['all', ...regions.map((region) => region.dataset.route)]);

  function selectRoute(route, { focus = false } = {}) {
    const selected = validRoutes.has(route) ? route : 'all';
    let visibleLandmarks = 0;

    filters.forEach((button) => {
      const active = button.dataset.route === selected;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
      if (active && focus) button.focus();
    });

    regions.forEach((region) => {
      const visible = selected === 'all' || region.dataset.route === selected;
      region.hidden = !visible;
      if (visible) visibleLandmarks += region.querySelectorAll('.landmark-list li').length;
    });

    const selectedButton = filters.find((button) => button.dataset.route === selected);
    const routeName = selected === 'all'
      ? 'all'
      : selectedButton.textContent.replace(/\d+\s*$/, '').trim().toLowerCase();
    status.textContent = selected === 'all'
      ? `Showing all ${visibleLandmarks} landmarks.`
      : `Showing ${visibleLandmarks} ${routeName} landmark${visibleLandmarks === 1 ? '' : 's'}.`;

    const url = new URL(window.location.href);
    if (selected === 'all') url.searchParams.delete('route');
    else url.searchParams.set('route', selected);
    window.history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
  }

  filters.forEach((button, index) => {
    button.addEventListener('click', () => selectRoute(button.dataset.route));
    button.addEventListener('keydown', (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const nextIndex = event.key === 'Home' ? 0
        : event.key === 'End' ? filters.length - 1
        : (index + (event.key === 'ArrowRight' ? 1 : -1) + filters.length) % filters.length;
      selectRoute(filters[nextIndex].dataset.route, { focus: true });
    });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && filters.some((button) => button.dataset.route !== 'all' && button.getAttribute('aria-pressed') === 'true')) {
      selectRoute('all', { focus: true });
    }
  });

  const requestedRoute = new URLSearchParams(window.location.search).get('route');
  selectRoute(requestedRoute || 'all');

  const navLinks = [...document.querySelectorAll('.masthead nav a[href^="#"]')];
  const observedSections = navLinks
    .map((link) => document.querySelector(link.getAttribute('href')))
    .filter(Boolean);

  if ('IntersectionObserver' in window) {
    const sectionObserver = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      navLinks.forEach((link) => {
        if (link.getAttribute('href') === `#${visible.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }, { rootMargin: '-20% 0px -65%', threshold: [0, .2, .5] });
    observedSections.forEach((section) => sectionObserver.observe(section));
  }

  let ticking = false;
  function updateJourneyProgress() {
    const distance = document.documentElement.scrollHeight - window.innerHeight;
    const progress = distance > 0 ? Math.min(100, Math.max(0, (window.scrollY / distance) * 100)) : 0;
    document.documentElement.style.setProperty('--journey-progress', progress.toFixed(2));
    ticking = false;
  }
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(updateJourneyProgress);
  }, { passive: true });
  updateJourneyProgress();
})();
