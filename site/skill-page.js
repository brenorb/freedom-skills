/* skill.html?s=<slug> — one template for all 31 skills, rendered from
   content/skills.js + content/skill-details.js. Unknown slug → a picker. */
(function () {
  'use strict';
  var FS = window.FS, root = document.getElementById('skill-root');
  if (!FS || !FS.skills || !root) return;
  var esc = FS.esc;
  var m = /[?&]s=([^&#]+)/.exec(location.search);
  var slug = m ? decodeURIComponent(m[1]) : '';
  var s = FS.bySlug[slug];
  var EXT = ' target="_blank" rel="noopener noreferrer"', NEW = '<span class="vh"> (opens in a new tab)</span>';
  function copyBtn(text, what, label, cls) { return '<button class="' + (cls || 'copy') + '" type="button" data-copy="' + esc(text) + '" data-what="' + esc(what) + '">' + (label || 'Copy') + '</button>'; }
  function cmd(text, what, big) { return '<div class="cmd' + (big ? ' big' : '') + '"><pre><code>' + esc(text) + '</code></pre>' + copyBtn(text, what) + '</div>'; }

  if (!s) {
    document.title = 'All 31 skills — Freedom Skills';
    var h = '<div class="picker-intro"><p class="kicker">Skill pages</p><h1>Pick a skill.</h1><p class="dek">' +
      (slug ? 'There’s no skill called “' + esc(slug) + '”. ' : '') + 'Every one of the 31 has its own page with a demo, prompts to try, and how to install it.</p></div>';
    FS.cats.forEach(function (c, ci) {
      var list = FS.ordered.filter(function (k) { return k.category === c.id; });
      h += '<section class="dept" aria-labelledby="p-' + c.id + '"><div class="dept-head"><p class="dno">Category ' + FS.num(ci + 1) + ' · ' + list.length + ' skills</p><h2 id="p-' + c.id + '" style="font-family:var(--display);font-size:1.6rem;margin:0;letter-spacing:-.02em">' + esc(c.name) + '</h2></div><ol class="entries">' +
        list.map(function (k) { return '<li class="entry"><span class="no" aria-hidden="true">' + FS.num(k.no) + '</span><div class="body"><h3 style="margin:0 0 .25rem;font-family:var(--display);font-size:1.22rem"><a href="skill.html?s=' + k.slug + '">' + esc(k.name) + '</a></h3><p>' + esc(k.tagline) + '</p></div></li>'; }).join('') +
        '</ol></section>';
    });
    root.innerHTML = h + '<p style="margin:2rem 0 0"><a href="index.html">← Back to the home page</a></p>';
    return;
  }

  var d = FS.details(slug), c = FS.catById[s.category];
  var i = FS.ordered.indexOf(s), prev = FS.ordered[(i - 1 + FS.ordered.length) % FS.ordered.length], next = FS.ordered[(i + 1) % FS.ordered.length];
  document.title = s.name + ' — Freedom Skills';
  var md = document.querySelector('meta[name=description]'); if (md) md.setAttribute('content', s.tagline);
  var byHand = 'git clone https://github.com/brenorb/freedom-skills\ncp -r freedom-skills/skills/' + slug + ' ~/.claude/skills/';
  var upHost = s.upstream.replace(/^https?:\/\//, '').replace(/\/$/, '');

  root.innerHTML =
    '<p class="crumbs"><a href="index.html">Home</a> / <a href="index.html#' + c.id + '">' + esc(c.name) + '</a> / ' + FS.num(s.no) + ' of 31</p>' +
    '<header class="sk-head"><span class="sk-no" aria-hidden="true">' + FS.num(s.no) + '</span><div>' +
      '<p class="kicker">' + esc(c.name) + '</p><h1>' + esc(s.name) + '</h1><p class="dek">' + esc(s.tagline) + '</p></div></header>' +
    '<div class="sk-grid"><div class="sk-main">' +
      '<section aria-labelledby="what-h" class="sk-what"><h2 id="what-h">What it’s for</h2><p>' + esc(d.what_for) + '</p></section>' +
      '<section aria-labelledby="demo-h"><h2 id="demo-h">Demo</h2><div id="player"></div></section>' +
      '<section aria-labelledby="ask-h"><h2 id="ask-h">Try asking</h2><ul class="prompts">' +
        d.prompts.map(function (p) { return '<li><q>' + esc(p) + '</q>' + copyBtn(p, 'prompt', 'Copy prompt', 'mini') + '</li>'; }).join('') +
      '</ul></section>' +
      (d.caveats.length ? '<section aria-labelledby="cav-h"><h2 id="cav-h">Caveats</h2><ul class="caveats">' + d.caveats.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></section>' : '') +
    '</div><aside class="sk-side" aria-label="Install and details">' +
      '<section aria-labelledby="in-h"><h2 id="in-h">Install</h2>' +
        '<p class="cmd-label">This skill</p>' + cmd(d.install, 'install command for ' + s.name, true) +
        '<p class="cmd-label">All 31 skills</p>' + cmd('npx skills add brenorb/freedom-skills', 'install command for all skills') +
        '<p class="cmd-label">By hand</p>' + cmd(byHand, 'both commands') +
      '</section>' +
      '<section aria-labelledby="need-h"><h2 id="need-h">Before you start</h2><dl>' +
        (d.needs ? '<dt>You need</dt><dd>' + esc(d.needs) + '</dd>' : '') +
        '<dt>Tool</dt><dd>' + esc(s.tool) + '</dd></dl></section>' +
      '<section aria-labelledby="links-h"><h2 id="links-h">Links</h2><ul class="links">' +
        '<li><a href="' + esc('https://github.com/brenorb/freedom-skills/blob/main/skills/' + slug + '/SKILL.md') + '"' + EXT + '>Read the skill on GitHub ↗<span>skills/' + esc(slug) + '/SKILL.md</span>' + NEW + '</a></li>' +
        '<li><a href="' + esc(s.upstream) + '"' + EXT + '>Upstream tool ↗<span>' + esc(upHost) + '</span>' + NEW + '</a></li>' +
      '</ul></section>' +
      '<section aria-labelledby="song-h"><h2 id="song-h">Theme song</h2>' +
        (d.music ? '<p>' + esc(d.music) + '</p>' :
        '<div class="song"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M9 18V5l11-2v13" stroke-linejoin="round"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/></svg><p><strong>Coming soon</strong>Songs are being made for some skills. This one doesn’t have one yet.</p></div>') +
      '</section>' +
    '</aside></div>' +
    '<nav class="pager" aria-label="More skills"><a class="prev" href="skill.html?s=' + prev.slug + '"><span class="d">← Previous · ' + FS.num(prev.no) + '</span><span class="t">' + esc(prev.name) + '</span></a>' +
      '<a class="next" href="skill.html?s=' + next.slug + '"><span class="d">Next · ' + FS.num(next.no) + ' →</span><span class="t">' + esc(next.name) + '</span></a></nav>';

  if (FS.Player) new FS.Player(document.getElementById('player'), { slug: slug, label: 'Simulated run of the ' + s.name + ' skill' });
})();
