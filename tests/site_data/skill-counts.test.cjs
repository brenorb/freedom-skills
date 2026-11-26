const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const root = resolve(__dirname, '../..');
const sharedScript = readFileSync(resolve(root, 'site/site.js'), 'utf8');
const skillScript = readFileSync(resolve(root, 'site/skill-page.js'), 'utf8');

function element() {
  const attributes = {};
  return {
    textContent: '', innerHTML: '', style: {},
    setAttribute(key, value) { attributes[key] = value; },
    getAttribute(key) { return attributes[key] ?? null; },
    classList: { add() {}, remove() {} },
  };
}

function display(html, count, search) {
  const pattern = /<span data-skill-count>(.*?)<\/span>/gs;
  const counters = [...html.matchAll(pattern)].map(element);
  const skillRoot = element();
  const document = {
    title: '', documentElement: element(), body: { appendChild() {} },
    querySelectorAll(selector) { return selector === '[data-skill-count]' ? counters : []; },
    querySelector() { return element(); },
    getElementById(id) { return id === 'skill-root' && search !== undefined ? skillRoot : null; },
    addEventListener() {}, createElement: element,
  };
  const window = {
    matchMedia() { return { matches: false, addEventListener() {} }; },
    FREEDOM_SKILLS: count === undefined ? undefined : {
      categories: [{ id: 'tools', name: 'Tools' }],
      skills: Array.from({ length: count }, (_, i) => ({
        slug: 'skill-' + i, name: 'Skill ' + i, category: 'tools',
        tagline: 'A skill', summary: 'An example skill', example_prompt: 'Do a task',
        tool: 'tool', upstream: 'https://example.com/tool',
      })),
    },
  };
  const context = vm.createContext({ window, document, location: { search }, setTimeout, clearTimeout });
  vm.runInContext(sharedScript, context, { filename: 'site.js' });
  if (search !== undefined) vm.runInContext(skillScript, context, { filename: 'skill-page.js' });
  let i = 0;
  return { document, skillRoot, counters, html: html.replace(pattern, () => counters[i++].textContent) };
}

for (const count of [2, 19, 38]) {
  test(`home and about display the loaded catalog total (${count})`, () => {
    for (const page of ['index.html', 'about.html']) {
      const result = display(readFileSync(resolve(root, 'site', page), 'utf8'), count);
      assert.ok(result.counters.length >= 2, `${page} should use shared count elements`);
      assert.ok(result.counters.every(counter => counter.textContent === count));
      assert.ok(result.html.includes(`Install all ${count} skills`));
    }
  });

  test(`picker title and copy display the catalog total (${count})`, () => {
    for (const search of ['', '?s=unknown']) {
      const result = display('', count, search);
      assert.equal(result.document.title, `All ${count} skills — Freedom Skills`);
      assert.ok(result.skillRoot.innerHTML.includes(`Every one of the ${count} has its own page`));
    }
  });

  test(`skill breadcrumb and install label display the catalog total (${count})`, () => {
    const result = display('', count, '?s=skill-0');
    assert.ok(result.skillRoot.innerHTML.includes(`01 of ${count}</p>`));
    assert.ok(result.skillRoot.innerHTML.includes(`All ${count} skills</p>`));
  });
}

test('missing catalog keeps readable copy without a stale total', () => {
  const result = display(readFileSync(resolve(root, 'site/about.html'), 'utf8'));
  const text = result.html.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ');
  assert.ok(text.includes('Install all skills'));
  assert.ok(result.counters.every(counter => counter.textContent === ''));
});
