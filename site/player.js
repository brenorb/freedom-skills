/* The Player — adapted from Rauno Freiberg v2 "Hold to Approve".
   One number t ∈ [0,100] drives the whole run, so playing and scrubbing share
   one code path. The transcript has a fixed height and streams like a chat:
   new lines arrive at the bottom, older ones scroll up, and it follows along
   unless you scroll up yourself. Simulation only — nothing runs. */
(function () {
  'use strict';
  var FS = window.FS;
  if (!FS) return;
  var mq = window.matchMedia('(prefers-reduced-motion: reduce)');
  function reduce() { return mq.matches; }
  function clamp(x, a, b) { return x < a ? a : x > b ? b : x; }
  var esc = FS.esc;

  var KIND = {
    you: 'You', ask: 'You', user: 'You', prompt: 'You',
    think: 'Thinks', plan: 'Plans', read: 'Reads', load: 'Loads', match: 'Skill', skill: 'Skill',
    run: 'Runs', tool: 'Runs', cmd: 'Runs', exec: 'Runs', command: 'Runs',
    check: 'Checks', verify: 'Checks', output: 'Output', out: 'Output', info: 'Note', note: 'Note',
    caveat: 'Caveat', warn: 'Caveat', warning: 'Caveat',
    confirm: 'Asks you', approve: 'Asks you', approval: 'Asks you', ask_user: 'Asks you',
    result: 'Done', done: 'Done', agent: 'Agent', say: 'Agent'
  };
  function kindLabel(k) { k = String(k || '').toLowerCase(); return KIND[k] || (k ? k.charAt(0).toUpperCase() + k.slice(1) : 'Step'); }
  function isApproval(st) { var k = String(st.kind || '').toLowerCase(); return !!st.action || k === 'confirm' || k === 'approve' || k === 'approval' || k === 'ask_user'; }

  var ICON_PLAY = '<svg class="i-play" viewBox="0 0 14 14" fill="currentColor" aria-hidden="true"><path d="M3.5 2.2v9.6a.5.5 0 0 0 .76.43l7.7-4.8a.5.5 0 0 0 0-.86l-7.7-4.8a.5.5 0 0 0-.76.43Z"/></svg>';
  var ICON_PAUSE = '<svg class="i-pause" viewBox="0 0 14 14" fill="currentColor" aria-hidden="true"><rect x="3" y="2" width="3" height="10"/><rect x="8" y="2" width="3" height="10"/></svg>';

  function Player(root, opts) {
    opts = opts || {};
    var self = this;
    var slugs = opts.slugs || [opts.slug];
    var slug = opts.slug || slugs[0];
    var uid = 'pl' + Math.random().toString(36).slice(2, 7);

    var chipsHTML = '';
    if (opts.chips) {
      chipsHTML = '<div class="pl-strip"><p class="pl-strip-label" id="' + uid + '-sl"><span>Pick a request</span><span class="pl-n"></span></p>' +
        '<div class="pl-chips-vp"><div class="pl-chips" role="radiogroup" aria-labelledby="' + uid + '-sl">' +
        slugs.map(function (s) { var k = FS.bySlug[s]; return '<button class="pl-chip" type="button" role="radio" aria-checked="false" tabindex="-1" data-slug="' + s + '">' + esc(k.name) + '</button>'; }).join('') +
        '</div></div></div>';
    }
    root.innerHTML =
      '<div class="player" role="region" aria-label="' + esc(opts.label || 'Simulated agent run') + '">' +
        '<div class="pl-bar"><span class="dot" aria-hidden="true"></span><span>Agent session</span><span class="sim">Simulation — nothing runs</span></div>' +
        chipsHTML +
        '<ol class="pl-log" tabindex="0" aria-label="Transcript"></ol>' +
        '<div class="pl-scrub">' +
          '<button class="pl-play" type="button" aria-pressed="false" aria-label="Play the run">' + ICON_PLAY + ICON_PAUSE + '</button>' +
          '<div class="pl-rail"><span class="bg"></span><span class="pr"></span><span class="ticks"></span><span class="th"></span>' +
            '<input type="range" min="0" max="100" step="0.5" value="0" aria-label="Run timeline" aria-describedby="' + uid + '-td"></div>' +
          '<span class="pl-pos" aria-hidden="true"></span>' +
          '<p class="vh" id="' + uid + '-td">Arrow keys jump between steps. Shift plus arrow keys scrub finely.</p>' +
        '</div>' +
        '<p class="vh" role="status" aria-live="polite"></p>' +
      '</div>';

    var q = function (s) { return root.querySelector(s); };
    var log = q('.pl-log'), playBtn = q('.pl-play'), range = q('.pl-rail input'), pr = q('.pl-rail .pr'), th = q('.pl-rail .th');
    var ticks = q('.pl-rail .ticks'), pos = q('.pl-pos'), status = q('[role=status]');
    var chips = Array.prototype.slice.call(root.querySelectorAll('.pl-chip')), nEl = q('.pl-n');

    var rows = [], B = [], t = 0, playing = false, raf = 0, approved = false, lastCur = -1, stick = true, progScroll = false;
    var demo, hold, fill, hl, ink, single, done, apprQ, interacted = false, holdTouched = false;
    var unitMs = 1300;

    function build() {
      var s = FS.bySlug[slug], d = FS.details(slug).demo;
      var steps = d.steps.slice(), ai = -1;
      for (var i = 0; i < steps.length; i++) if (isApproval(steps[i])) { ai = i; break; }
      var appr, after = [];
      if (ai === -1) appr = { kind: 'confirm', text: 'Ready. Approve this run?', action: 'Approve' };
      else { appr = steps[ai]; after = steps.slice(ai + 1); steps = steps.slice(0, ai); }
      demo = { prompt: d.prompt, steps: steps, appr: appr, after: after, result: d.result };

      var h = '<li class="pl-st" data-i="0"><span class="pl-lab">You</span><div class="pl-body"><p class="pl-say"><span class="typed"></span><span class="pl-caret" aria-hidden="true"></span></p></div></li>';
      steps.forEach(function (st, i) {
        h += '<li class="pl-st k-' + esc(String(st.kind || 'step').toLowerCase()) + '" data-i="' + (i + 1) + '" hidden><span class="pl-lab">' + esc(kindLabel(st.kind)) + '</span><div class="pl-body"><p>' + esc(st.text || '') + '</p>' +
          (st.cmd ? '<div class="pl-cmd">' + esc(st.cmd) + '</div>' : '') + '</div></li>';
      });
      var verb = appr.action || 'Approve';
      h += '<li class="pl-st k-confirm" data-i="' + (steps.length + 1) + '" hidden><span class="pl-lab">Asks you</span><div class="pl-body"><div class="pl-appr">' +
        '<p class="pl-appr-q">' + esc(appr.text || 'Ready. Approve this run?') + '</p>' +
        '<div class="pl-appr-row"><button class="hold" type="button" aria-disabled="true" aria-describedby="' + uid + '-hd"><span class="fill"></span><span class="hl">Hold to ' + esc(lc(verb)) + '</span><span class="hl-ink" aria-hidden="true">Hold to ' + esc(lc(verb)) + '</span></button>' +
        '<label class="single"><input type="checkbox"> Single press</label></div>' +
        '<p class="vh" id="' + uid + '-hd">Press and hold for one second with the pointer, or hold Space or Enter. Turn on Single press to approve with one press.</p>' +
        '<p class="pl-note">Simulation — nothing here sends, pays or publishes.</p>' +
        '<div class="pl-done" hidden>' +
          after.map(function (st) { return '<p><strong>' + esc(kindLabel(st.kind)) + ':</strong> ' + esc(st.text || '') + '</p>' + (st.cmd ? '<div class="pl-cmd">' + esc(st.cmd) + '</div>' : ''); }).join('') +
          '<p><strong>' + (demo.result ? 'Result:</strong> ' + esc(demo.result) : 'Approved.</strong> In a real run, this is where your agent acts — and only now.') + '</p>' +
          '<div class="pl-acts"><button class="mini solid" type="button" data-copy="' + esc(FS.install(slug)) + '" data-what="install command for ' + esc(s.name) + '">Copy install for ' + esc(s.name) + '</button>' +
          (opts.skillLink ? '<a class="mini" href="skill.html?s=' + slug + '">' + esc(s.name) + ' skill page →</a>' : '') +
          '<button class="mini again" type="button">Run again</button></div>' +
        '</div></div></div></li>';
      log.innerHTML = h;
      rows = Array.prototype.slice.call(log.querySelectorAll('.pl-st'));

      // timeline weights: typing scales with the prompt, commands get a beat more
      var w = [clamp(demo.prompt.length / 38, 1.2, 3)];
      steps.forEach(function (st) { w.push(st.cmd ? 1.35 : 1); });
      w.push(1);
      var total = w.reduce(function (a, b) { return a + b; }, 0), acc = 0;
      B = [0];
      for (var j = 0; j < w.length - 1; j++) { acc += w[j]; B.push(acc / total * 100); }
      B.push(100);
      unitMs = 1250;
      self.dur = total * unitMs;
      ticks.innerHTML = B.slice(1, -1).map(function (b) { return '<span class="tk" style="left:' + b.toFixed(2) + '%"></span>'; }).join('');

      hold = log.querySelector('.hold'); fill = hold.querySelector('.fill'); hl = hold.querySelector('.hl'); ink = hold.querySelector('.hl-ink');
      single = log.querySelector('.single input'); done = log.querySelector('.pl-done'); apprQ = log.querySelector('.pl-appr-q');
      wireHold();
      log.querySelector('.again').addEventListener('click', function () { resetApproval(); stick = true; setT(0); play(); });
      approved = false; lastCur = -1; stick = true;
    }
    function lc(s) { return s.charAt(0).toLowerCase() + s.slice(1); }

    function curAt(x) { for (var i = B.length - 2; i > 0; i--) if (x >= B[i]) return i; return 0; }
    function render(entering) {
      var P = demo.prompt, tp = clamp(t / (B[1] * 0.92), 0, 1), n = Math.round(P.length * tp);
      var typed = rows[0].querySelector('.typed');
      typed.textContent = '“' + P.slice(0, n) + (n === P.length ? '”' : '');
      rows[0].querySelector('.pl-say').classList.toggle('typing', n < P.length && t > 0);
      var cur = curAt(t);
      rows.forEach(function (r, i) {
        var vis = i === 0 || t >= B[i];
        if (r.hidden === vis) {
          r.hidden = !vis;
          if (vis && entering && !reduce()) { r.classList.remove('enter'); void r.offsetWidth; r.classList.add('enter'); }
        }
        r.classList.toggle('cur', i === cur);
      });
      pr.style.width = t + '%'; th.style.left = t + '%'; range.value = t;
      var total = rows.length;
      range.setAttribute('aria-valuetext', 'Step ' + (cur + 1) + ' of ' + total);
      pos.textContent = 'Step ' + (cur + 1) + ' / ' + total;
      var ready = t >= 100;
      hold.setAttribute('aria-disabled', String(!ready && !approved));
      hold.classList.toggle('pulse', ready && !approved && !holdTouched);
      if (!ready && approved) resetApproval();
      if (cur !== lastCur) {
        lastCur = cur;
        status.textContent = cur === 0 ? 'You asked: ' + P : (cur === rows.length - 1 ? 'The agent stops and asks you: ' + (demo.appr.text || 'Approve?') : rows[cur].querySelector('.pl-lab').textContent + ': ' + rows[cur].querySelector('.pl-body p').textContent);
      }
      follow();
    }
    function follow() {
      if (!stick) return;
      progScroll = true;
      log.scrollTop = log.scrollHeight;
      requestAnimationFrame(function () { progScroll = false; });
    }
    log.addEventListener('scroll', function () {
      if (progScroll) return;
      stick = log.scrollHeight - log.scrollTop - log.clientHeight < 28;
    }, { passive: true });

    function setT(x, entering) { t = clamp(x, 0, 100); render(entering); }
    function play() {
      markInteracted();
      if (reduce()) { pause(); setT(100); return; }
      if (t >= 100) { stick = true; setT(0); }
      playing = true; playBtn.setAttribute('aria-pressed', 'true'); playBtn.setAttribute('aria-label', 'Pause the run');
      var last = performance.now();
      cancelAnimationFrame(raf);
      (function tick(now) {
        if (!playing) return;
        var dt = now - last; last = now;
        setT(t + dt / self.dur * 100, true);
        if (t >= 100) { pause(); return; }
        raf = requestAnimationFrame(tick);
      })(last);
    }
    function pause() { playing = false; cancelAnimationFrame(raf); playBtn.setAttribute('aria-pressed', 'false'); playBtn.setAttribute('aria-label', 'Play the run'); }
    function markInteracted() { if (!interacted) { interacted = true; playBtn.classList.remove('pulse'); } }
    playBtn.addEventListener('click', function () { markInteracted(); playing ? pause() : play(); });
    range.addEventListener('input', function () { markInteracted(); pause(); stick = true; setT(+range.value); });
    range.addEventListener('keydown', function (e) {
      if (e.shiftKey || e.altKey || e.metaKey || e.ctrlKey) return;
      var k = e.key, to;
      if (k === 'ArrowRight' || k === 'ArrowUp') to = B.filter(function (b) { return b > t + 0.01; })[0];
      else if (k === 'ArrowLeft' || k === 'ArrowDown') { var lo = B.filter(function (b) { return b < t - 0.01; }); to = lo[lo.length - 1]; }
      else return;
      e.preventDefault(); markInteracted(); pause(); stick = true;
      if (to !== undefined) setT(to);
    });

    /* Hold to approve: progress fills while held; let go early and it eases back. */
    function wireHold() {
      var HOLD = 1000, p = 0, holding = false, hRaf = 0, back = 0, heldAt = 0;
      function draw() { var qx = clamp(p, 0, 1); fill.style.transform = 'scaleX(' + qx.toFixed(4) + ')'; ink.style.clipPath = 'inset(0 ' + ((1 - qx) * 100).toFixed(2) + '% 0 0)'; }
      function label(txt) { hl.textContent = txt; ink.textContent = txt; }
      var verb = 'Hold to ' + lc(demo.appr.action || 'Approve');
      function start() {
        holdTouched = true; hold.classList.remove('pulse');
        if (approved || hold.getAttribute('aria-disabled') === 'true') return;
        if (single.checked) { approve(); return; }
        if (holding) return;
        holding = true; heldAt = performance.now(); cancelAnimationFrame(back);
        label('Keep holding…');
        var last = performance.now();
        (function tick(now) {
          if (!holding) return;
          p += (now - last) / HOLD; last = now;
          if (p >= 1) { p = 1; draw(); approve(); return; }
          draw(); hRaf = requestAnimationFrame(tick);
        })(last);
      }
      function end() {
        if (!holding) return;
        holding = false; cancelAnimationFrame(hRaf);
        if (approved) return;
        label(verb);
        if (reduce()) { p = 0; draw(); return; }
        var from = p, t0 = performance.now();
        (function tick(now) { var k = clamp((now - t0) / 260, 0, 1); p = from * (1 - k) * (1 - k); draw(); if (k < 1) back = requestAnimationFrame(tick); })(t0);
      }
      function approve() {
        holding = false; cancelAnimationFrame(hRaf); approved = true; p = 1; draw();
        hold.setAttribute('data-done', ''); hold.classList.remove('pulse');
        label((demo.appr.action || 'Approved') + ' ✓');
        done.hidden = false;
        status.textContent = 'Approved. This is a simulation — nothing was sent.';
        stick = true; follow();
      }
      self._resetHold = function () { approved = false; p = 0; draw(); hold.removeAttribute('data-done'); label(verb); done.hidden = true; };
      hold.addEventListener('pointerdown', function (e) { if (e.button !== 0) return; e.preventDefault(); hold.focus({ preventScroll: true }); try { hold.setPointerCapture(e.pointerId); } catch (x) {} start(); });
      ['pointerup', 'pointercancel', 'lostpointercapture', 'blur'].forEach(function (ev) { hold.addEventListener(ev, end); });
      hold.addEventListener('contextmenu', function (e) { e.preventDefault(); });
      hold.addEventListener('keydown', function (e) { if (e.key !== ' ' && e.key !== 'Enter') return; e.preventDefault(); if (!e.repeat) start(); });
      hold.addEventListener('keyup', function (e) { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); end(); } });
      hold.addEventListener('click', function (e) {
        if (e.detail !== 0 || approved || holding) return; // assistive tech sends a bare click
        if (hold.getAttribute('aria-disabled') === 'true') { status.textContent = 'The run hasn’t reached the approval step yet.'; return; }
        if (single.checked) { approve(); return; }
        if (performance.now() - heldAt > 300) status.textContent = 'Hold for one second, or turn on Single press to approve with one press.';
      });
    }
    function resetApproval() { if (self._resetHold) self._resetHold(); approved = false; }

    /* chips: a radiogroup with roving tabindex */
    function syncChips(o) {
      if (!chips.length) return;
      var i = slugs.indexOf(slug);
      chips.forEach(function (c, j) { c.setAttribute('aria-checked', String(j === i)); c.tabIndex = j === i ? 0 : -1; });
      nEl.textContent = (i + 1) + ' / ' + slugs.length;
      var c = chips[i], vp = c.parentNode.parentNode;
      var cr = c.getBoundingClientRect(), vr = vp.getBoundingClientRect();
      if (cr.left < vr.left + 20) vp.scrollLeft -= (vr.left + 20 - cr.left);
      else if (cr.right > vr.right - 28) vp.scrollLeft += (cr.right - vr.right + 28);
      if (o && o.focus) c.focus({ preventScroll: true });
    }
    chips.forEach(function (c, i) {
      c.addEventListener('click', function () { self.load(slugs[i], { play: true }); });
      c.addEventListener('keydown', function (e) {
        var n = chips.length, to = null;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') to = (i + 1) % n;
        else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') to = (i - 1 + n) % n;
        else if (e.key === 'Home') to = 0; else if (e.key === 'End') to = n - 1;
        if (to !== null) { e.preventDefault(); self.load(slugs[to], { play: true, focus: true }); }
      });
    });

    this.load = function (s, o) {
      o = o || {};
      pause(); slug = s; build(); syncChips(o);
      if (o.play) { markInteracted(); setT(0); play(); } else setT(reduce() ? 100 : (o.t || 0));
    };
    this.root = root;

    // boot: show the finished run for reduced motion; otherwise play once when on screen
    this.load(slug, { t: reduce() ? 100 : 0 });
    if (!reduce()) {
      playBtn.classList.add('pulse');
      var started = false, go = function () { if (!started && !interacted) { started = true; play(); interacted = false; playBtn.classList.add('pulse'); } };
      if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { go(); io.disconnect(); } }, { threshold: 0.35 });
        io.observe(root);
      } else go();
    }
  }
  FS.Player = Player;
})();
