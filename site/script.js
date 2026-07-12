(() => {
  const controls = [...document.querySelectorAll('.path-control')];
  const skills = [...document.querySelectorAll('.skill')];
  const routeLabel = document.querySelector('#route-label');
  const routeDetail = document.querySelector('#route-detail');

  if (!controls.length || !skills.length || !routeLabel || !routeDetail) return;

  const routes = {
    all: ['The whole commons', '15 capabilities are in view.'],
    communicate: ['Communicate & coordinate', '3 capabilities support speaking, sharing, and organizing.'],
    protect: ['Protect sensitive work', '5 capabilities help reduce exposure and strengthen resilience.'],
    fund: ['Move value & sustain work', '5 capabilities support self-custodial payments and open commerce.'],
    preserve: ['Research, share & preserve', '5 capabilities help evidence remain useful and reachable.'],
    build: ['Build better tools', '6 capabilities support safer, more sovereign products.']
  };

  const setRoute = (outcome, updateUrl = true) => {
    const next = routes[outcome] ? outcome : 'all';

    controls.forEach((control) => {
      const selected = control.dataset.outcome === next;
      control.classList.toggle('is-active', selected);
      control.setAttribute('aria-pressed', String(selected));
    });

    let count = 0;
    skills.forEach((skill) => {
      const outcomes = skill.dataset.outcomes.split(' ');
      const visible = next === 'all' || outcomes.includes(next);
      skill.classList.toggle('is-hidden', !visible);
      skill.setAttribute('aria-hidden', String(!visible));
      if (visible) count += 1;
    });

    routeLabel.textContent = routes[next][0];
    routeDetail.textContent = routes[next][1].replace(/^\d+/, String(count));

    if (updateUrl) {
      const url = new URL(window.location.href);
      if (next === 'all') url.searchParams.delete('path');
      else url.searchParams.set('path', next);
      window.history.replaceState({ path: next }, '', url);
    }
  };

  controls.forEach((control, index) => {
    control.addEventListener('click', () => setRoute(control.dataset.outcome));
    control.addEventListener('keydown', (event) => {
      if (!['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      let nextIndex = index;
      if (event.key === 'ArrowRight') nextIndex = (index + 1) % controls.length;
      if (event.key === 'ArrowLeft') nextIndex = (index - 1 + controls.length) % controls.length;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = controls.length - 1;
      controls[nextIndex].focus();
      setRoute(controls[nextIndex].dataset.outcome);
    });
  });

  const initialPath = new URL(window.location.href).searchParams.get('path') || 'all';
  setRoute(initialPath, false);
})();
