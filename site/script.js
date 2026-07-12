(() => {
  'use strict';

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

  const setupScroll = () => {
    const header = document.querySelector('.site-header');
    const meter = document.querySelector('.scroll-meter i');
    let previousY = window.scrollY;
    let ticking = false;

    const paint = () => {
      const y = window.scrollY;
      const distance = Math.max(1, document.documentElement.scrollHeight - innerHeight);
      meter.style.height = `${clamp(y / distance, 0, 1) * 100}%`;
      header.classList.toggle('is-solid', y > 32);
      header.classList.toggle('is-hidden', y > previousY && y > 420 && Math.abs(y - previousY) > 4);
      previousY = y;
      ticking = false;
    };

    addEventListener('scroll', () => {
      if (!ticking) requestAnimationFrame(paint);
      ticking = true;
    }, { passive: true });
    paint();
  };

  const setupMenu = () => {
    const toggle = document.querySelector('.nav-toggle');
    const nav = document.querySelector('.primary-nav');
    if (!toggle || !nav) return;

    const close = () => {
      toggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('menu-open');
    };

    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open));
      document.body.classList.toggle('menu-open', open);
    });
    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) close();
    });
    addEventListener('keydown', (event) => {
      if (event.key === 'Escape') close();
    });
  };

  const setupCursor = () => {
    if (!finePointer.matches) return;
    const cursor = document.querySelector('.cursor-orbit');
    if (!cursor) return;
    let currentX = -100;
    let currentY = -100;
    let targetX = -100;
    let targetY = -100;

    addEventListener('pointermove', (event) => {
      targetX = event.clientX;
      targetY = event.clientY;
      cursor.style.opacity = '1';
    }, { passive: true });
    document.addEventListener('pointerover', (event) => {
      cursor.classList.toggle('is-link', Boolean(event.target.closest('a, button')));
    });
    document.addEventListener('pointerleave', () => { cursor.style.opacity = '0'; });

    const follow = () => {
      currentX += (targetX - currentX) * .16;
      currentY += (targetY - currentY) * .16;
      cursor.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
      requestAnimationFrame(follow);
    };
    follow();
  };

  const setupReveals = () => {
    const targets = document.querySelectorAll('.chapter-index, .thesis-grid, .tension-line, .relay-head, .relay-machine, .pathfinder-head, .path-controls, .skill-constellation, .proof-head, .proof-numbers, .roadmap, .commons-copy');
    if (reducedMotion.matches || !('IntersectionObserver' in window)) return;
    targets.forEach((target) => target.classList.add('js-reveal'));
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    targets.forEach((target) => observer.observe(target));
  };

  const setupFilters = () => {
    const tabs = [...document.querySelectorAll('[role="tab"][data-path]')];
    const skills = [...document.querySelectorAll('.skill[data-path]')];
    const count = document.querySelector('#skill-count');
    if (!tabs.length || !skills.length) return;

    const apply = (path, updateUrl = true) => {
      if (!tabs.some((tab) => tab.dataset.path === path)) path = 'all';
      let visible = 0;
      tabs.forEach((tab) => {
        const selected = tab.dataset.path === path;
        tab.setAttribute('aria-selected', String(selected));
        tab.tabIndex = selected ? 0 : -1;
      });
      skills.forEach((skill, index) => {
        const match = path === 'all' || skill.dataset.path.split(' ').includes(path);
        skill.classList.toggle('is-hidden', !match);
        skill.classList.remove('is-arriving');
        if (match) {
          visible += 1;
          if (!reducedMotion.matches) {
            skill.style.animationDelay = `${Math.min(index, 7) * 35}ms`;
            requestAnimationFrame(() => skill.classList.add('is-arriving'));
          }
        }
      });
      count.textContent = String(visible);
      if (updateUrl) {
        const url = new URL(location.href);
        path === 'all' ? url.searchParams.delete('path') : url.searchParams.set('path', path);
        history.replaceState({}, '', url);
      }
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => apply(tab.dataset.path));
      tab.addEventListener('keydown', (event) => {
        let next = index;
        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % tabs.length;
        else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index - 1 + tabs.length) % tabs.length;
        else if (event.key === 'Home') next = 0;
        else if (event.key === 'End') next = tabs.length - 1;
        else return;
        event.preventDefault();
        tabs[next].focus();
        apply(tabs[next].dataset.path);
      });
    });
    apply(new URL(location.href).searchParams.get('path') || 'all', false);
  };

  const setupTrust = () => {
    const steps = [...document.querySelectorAll('[data-trust-step]')];
    const trust = document.querySelector('.trust');
    if (!steps.length || !trust || !('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver((entries) => {
      const nearest = entries.filter((entry) => entry.isIntersecting)
        .sort((a, b) => Math.abs(a.boundingClientRect.top - innerHeight * .5) - Math.abs(b.boundingClientRect.top - innerHeight * .5))[0];
      if (!nearest) return;
      steps.forEach((step) => step.classList.toggle('is-active', step === nearest.target));
      trust.style.setProperty('--trust-progress', String(steps.indexOf(nearest.target) / (steps.length - 1)));
    }, { rootMargin: '-28% 0px -28% 0px', threshold: .05 });
    steps.forEach((step) => observer.observe(step));
    steps[0].classList.add('is-active');
  };

  const setupMagnetics = () => {
    if (!finePointer.matches || reducedMotion.matches) return;
    document.querySelectorAll('.magnetic').forEach((element) => {
      element.addEventListener('pointermove', (event) => {
        const bounds = element.getBoundingClientRect();
        const x = (event.clientX - bounds.left - bounds.width / 2) * .12;
        const y = (event.clientY - bounds.top - bounds.height / 2) * .16;
        element.style.transform = `translate3d(${x}px, ${y}px, 0)`;
      });
      element.addEventListener('pointerleave', () => { element.style.transform = ''; });
    });
  };

  const createEmberField = (canvas, options = {}) => {
    if (!canvas) return () => {};
    const context = canvas.getContext('2d');
    const embers = [];
    let width = 0;
    let height = 0;
    let frame = 0;
    let visible = true;
    const density = options.density || 8500;
    const colors = options.colors || ['#ff6b35', '#ffe378', '#8ad6dc'];

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const ratio = Math.min(devicePixelRatio || 1, 2);
      width = rect.width;
      height = rect.height;
      canvas.width = Math.max(1, Math.floor(width * ratio));
      canvas.height = Math.max(1, Math.floor(height * ratio));
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      const wanted = clamp(Math.floor(width * height / density), 34, 145);
      while (embers.length < wanted) embers.push(seed(true));
      embers.length = wanted;
    };

    const seed = (randomY = false) => ({
      x: Math.random() * width,
      y: randomY ? Math.random() * height : height + Math.random() * 40,
      radius: .45 + Math.random() * 2.2,
      velocity: .12 + Math.random() * .44,
      drift: (Math.random() - .5) * .2,
      phase: Math.random() * Math.PI * 2,
      alpha: .08 + Math.random() * .5,
      color: colors[Math.floor(Math.random() * colors.length)]
    });

    const draw = (time = 0) => {
      frame = requestAnimationFrame(draw);
      if (!visible || reducedMotion.matches) return;
      context.clearRect(0, 0, width, height);
      embers.forEach((ember, index) => {
        ember.y -= ember.velocity;
        ember.x += ember.drift + Math.sin(time * .0005 + ember.phase) * .08;
        if (ember.y < -12 || ember.x < -20 || ember.x > width + 20) embers[index] = seed();
        context.globalAlpha = ember.alpha * (.62 + Math.sin(time * .002 + ember.phase) * .38);
        context.fillStyle = ember.color;
        context.beginPath();
        context.arc(ember.x, ember.y, ember.radius, 0, Math.PI * 2);
        context.fill();
      });
      context.globalAlpha = 1;
    };

    const observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; });
    observer.observe(canvas);
    resize();
    if (reducedMotion.matches) {
      context.fillStyle = 'rgba(255,227,120,.25)';
      embers.slice(0, 40).forEach((ember) => context.fillRect(ember.x, ember.y, 2, 2));
    } else frame = requestAnimationFrame(draw);
    addEventListener('resize', resize, { passive: true });
    return () => { cancelAnimationFrame(frame); observer.disconnect(); };
  };

  setupScroll();
  setupMenu();
  setupCursor();
  setupReveals();
  setupFilters();
  setupTrust();
  setupMagnetics();
  createEmberField(document.querySelector('#ember-field'));
  createEmberField(document.querySelector('#commons-field'), {
    density: 7000,
    colors: ['#ff6b35', '#ffe378', '#96d83f', '#8ad6dc']
  });
})();
