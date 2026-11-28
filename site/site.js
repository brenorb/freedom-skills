/* Shared behaviour for all three pages: data helpers, theme toggle, copy,
   toast, skill finder. Everything works over file:// — no fetch(). */
(function () {
  'use strict';
  var D = window.FREEDOM_SKILLS;
  var DET = window.FREEDOM_SKILL_DETAILS || {};
  var REPO = 'https://github.com/brenorb/freedom-skills';
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  var FS = window.FS = { esc: esc, repo: REPO };
  if (D) {
    FS.skills = D.skills;
    Array.prototype.forEach.call(document.querySelectorAll('[data-skill-count]'), function (element) {
      element.textContent = D.skills.length;
    });
    FS.cats = D.categories;
    FS.bySlug = {};
    FS.catById = {};
    D.categories.forEach(function (c) { FS.catById[c.id] = c; });
    // Number skills in category order, like the issue's contents.
    var order = [];
    D.categories.forEach(function (c) { D.skills.forEach(function (s) { if (s.category === c.id) order.push(s); }); });
    FS.ordered = order;
    order.forEach(function (s, i) { FS.bySlug[s.slug] = s; s.no = i + 1; });
    FS.num = function (n) { return (n < 10 ? '0' : '') + n; };
    FS.install = function (slug) { return 'npx skills add brenorb/freedom-skills -s ' + slug; };
    // Details come from content/skill-details.js. Where a field is missing, fall
    // back to what skills.js says — nothing invented.
    FS.details = function (slug) {
      var s = FS.bySlug[slug], d = DET[slug] || {};
      var demo = d.demo && d.demo.steps && d.demo.steps.length ? d.demo : {
        prompt: s.example_prompt,
        steps: [
          { kind: 'skill', text: 'Matched the ' + s.name + ' skill. Its full instructions load only now, when they are relevant.' },
          { kind: 'run', text: 'Follows the tested workflow with ' + s.tool + '.' },
          { kind: 'caveat', text: 'Surfaces what could go wrong before anything is sent, paid or published — then stops.' }
        ],
        result: ''
      };
      if (!demo.prompt) demo.prompt = s.example_prompt;
      return {
        install: d.install || FS.install(slug),
        what_for: d.what_for || s.summary,
        prompts: d.prompts && d.prompts.length ? d.prompts : [s.example_prompt],
        demo: demo,
        caveats: d.caveats || [],
        needs: d.needs || '',
        music: d.music || null
      };
    };
  }

  /* ---------- theme toggle ---------- */
  var root = document.documentElement;
  var dq = window.matchMedia('(prefers-color-scheme: dark)');
  function effective() { var a = root.getAttribute('data-theme'); return a === 'dark' || a === 'light' ? a : (dq.matches ? 'dark' : 'light'); }
  function syncToggle() {
    var dark = effective() === 'dark';
    Array.prototype.forEach.call(document.querySelectorAll('.theme-toggle'), function (b) {
      b.setAttribute('aria-pressed', String(dark));
      b.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
      b.title = dark ? 'Switch to light mode' : 'Switch to dark mode';
    });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.theme-toggle');
    if (!b) return;
    var next = effective() === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('fs-theme', next); } catch (x) {}
    syncToggle();
  });
  if (dq.addEventListener) dq.addEventListener('change', syncToggle);
  if ('MutationObserver' in window) new MutationObserver(syncToggle).observe(root, { attributes: true, attributeFilter: ['data-theme'] });
  syncToggle();

  /* ---------- toast + clipboard ---------- */
  var toast = document.createElement('div');
  toast.className = 'toast'; toast.setAttribute('role', 'status'); toast.setAttribute('aria-live', 'polite');
  document.body.appendChild(toast);
  var tT = 0;
  function say(m) { toast.textContent = m; toast.classList.add('show'); clearTimeout(tT); tT = setTimeout(function () { toast.classList.remove('show'); }, 1700); }
  FS.say = say;
  function legacyCopy(text) {
    var ta = document.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none';
    document.body.appendChild(ta); ta.select();
    var ok = false; try { ok = document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta); return ok;
  }
  function copyText(t) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(t).then(function () { return true; }, function () { return legacyCopy(t); });
    return Promise.resolve(legacyCopy(t));
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-copy]');
    if (!b) return;
    var text = b.getAttribute('data-copy'), what = b.getAttribute('data-what') || 'command';
    copyText(text).then(function (ok) {
      if (!ok) { say('Couldn’t reach the clipboard — select the text and copy it'); return; }
      var old = b.getAttribute('data-label') || b.textContent;
      b.setAttribute('data-label', old);
      b.setAttribute('data-state', 'copied');
      b.textContent = 'Copied';
      say('Copied ' + what);
      setTimeout(function () { b.textContent = b.getAttribute('data-label'); b.removeAttribute('data-state'); }, 1600);
    });
  });

  /* ---------- comic panels ease in when scrolled to (phones) ---------- */
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var panels = Array.prototype.slice.call(document.querySelectorAll('.panel'));
    var below = panels.filter(function (p) { return p.getBoundingClientRect().top > window.innerHeight; });
    if (below.length) {
      below.forEach(function (p) { p.classList.add('later'); });
      var io = new IntersectionObserver(function (en) { en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } }); }, { threshold: 0.2 });
      below.forEach(function (p) { io.observe(p); });
    }
  }

  /* ---------- skill finder (home) ---------- */
  var input = document.getElementById('q');
  if (input && D) {
    var list = document.getElementById('results'), stat = document.getElementById('q-status');
    var hay = FS.ordered.map(function (s) {
      var d = FS.details(s.slug), c = FS.catById[s.category];
      return [s.name, s.slug, s.tagline, s.summary, s.tool, c.name, d.prompts.join(' ')].join('   ').toLowerCase();
    });
    var connectorHay = (D.connectors || []).map(function (c) {
      return [c.name, c.slug, c.tagline, (c.works_with || []).join(' '), c.upstream, c.prompt].join('   ').toLowerCase();
    });
    function hi(text, terms) {
      var out = esc(text);
      terms.forEach(function (t) { if (t.length < 2) return; out = out.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); });
      return out;
    }
    function run() {
      var v = input.value.trim().toLowerCase();
      if (!v) { list.hidden = true; list.innerHTML = ''; stat.textContent = ''; return; }
      var terms = v.split(/\s+/);
      var hits = FS.ordered.filter(function (s, i) { return terms.every(function (t) { return hay[i].indexOf(t) !== -1; }); });
      var connectorHits = (D.connectors || []).filter(function (c, i) { return terms.every(function (t) { return connectorHay[i].indexOf(t) !== -1; }); });
      var count = hits.length + connectorHits.length;
      stat.textContent = count ? count + (count === 1 ? ' result matches' : ' results match') + ' “' + input.value.trim() + '”' : 'Nothing matches “' + input.value.trim() + '”. Try a tool (White Noise, Signal, Lightning) or a verb (pay, archive, publish).';
      list.innerHTML = hits.map(function (s) {
        return '<li class="res"><div><h4><a href="skill.html?s=' + s.slug + '"><span class="no">' + FS.num(s.no) + '</span>' + hi(s.name, terms) + '</a></h4><p>' + hi(s.tagline, terms) + '</p></div>' +
          '<div class="acts"><button class="mini solid" type="button" data-copy="' + esc(FS.install(s.slug)) + '" data-what="install command for ' + esc(s.name) + '">Copy install</button>' +
          '<a class="mini" href="skill.html?s=' + s.slug + '">Skill page</a>' +
          '<a class="mini" href="' + esc(s.url) + '" target="_blank" rel="noopener noreferrer">GitHub ↗<span class="vh"> (opens in a new tab)</span></a></div></li>';
      }).join('') + connectorHits.map(function (c) {
        return '<li class="res"><div><h4><a href="#connector-' + esc(c.slug) + '"><span class="no">C</span>' + hi(c.name, terms) + '</a></h4><p>' + hi(c.tagline, terms) + '</p></div>' +
          '<div class="acts"><button class="mini solid" type="button" data-copy="' + esc(c.prompt) + '" data-what="setup prompt for ' + esc(c.name) + '">Copy prompt</button>' +
          '<a class="mini" href="' + esc(c.prompt_url) + '" target="_blank" rel="noopener noreferrer">Read prompt ↗<span class="vh"> (opens in a new tab)</span></a></div></li>';
      }).join('');
      list.hidden = !count;
    }
    input.addEventListener('input', run);
    input.addEventListener('keydown', function (e) { if (e.key === 'Escape') { input.value = ''; run(); } });
    var form = input.closest('form');
    if (form) form.addEventListener('submit', function (e) { e.preventDefault(); var a = list.querySelector('a'); if (a) a.focus(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && !/input|textarea|select/i.test(document.activeElement.tagName)) { e.preventDefault(); input.focus(); }
    });
  }
})();
