import { access, readFile, stat } from 'node:fs/promises';
import { constants } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const html = await readFile(resolve(here, 'index.html'), 'utf8');
const css = await readFile(resolve(here, 'styles.css'), 'utf8');
const script = resolve(here, 'script.js');
const failures = [];

const expect = (condition, message) => {
  if (!condition) failures.push(message);
};

for (const landmark of ['<header', '<main', '<nav', '<footer', '<h1']) {
  expect(html.includes(landmark), `Missing landmark: ${landmark}`);
}

const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
expect(ids.length === new Set(ids).size, 'Document contains duplicate IDs');

const skillCards = [...html.matchAll(/class="skill"/g)].length;
expect(skillCards === 15, `Expected 15 skill cards, found ${skillCards}`);
expect(html.includes('class="skip-link"'), 'Missing skip link');
expect(html.includes('aria-live="polite"'), 'Missing live filter status');
expect(html.includes('role="tablist"'), 'Missing outcome tablist');
expect(css.includes('prefers-reduced-motion'), 'Missing reduced-motion styles');
expect(html.includes('<noscript>'), 'Missing no-JavaScript explanation');

const runtimeRemote = [...html.matchAll(/(?:src|href|data)="(https?:\/\/[^"#]+)"/g)]
  .map((match) => match[1])
  .filter((url) => /\.(?:js|css|woff2?|ttf)(?:\?|$)/i.test(url));
expect(runtimeRemote.length === 0, `Remote runtime dependencies found: ${runtimeRemote.join(', ')}`);

const localReferences = [...html.matchAll(/(?:src|href|data)="([^"#?]+)"/g)]
  .map((match) => match[1])
  .filter((reference) => !/^(?:https?:|mailto:|tel:)/.test(reference));

for (const reference of new Set(localReferences)) {
  try {
    const target = resolve(here, reference);
    await access(target, constants.R_OK);
    expect((await stat(target)).isFile(), `Local reference must resolve to a file: ${reference}`);
  } catch {
    failures.push(`Broken local reference: ${reference}`);
  }
}

const syntax = spawnSync(process.execPath, ['--check', script], { encoding: 'utf8' });
expect(syntax.status === 0, syntax.stderr.trim() || 'JavaScript syntax check failed');

if (failures.length) {
  console.error(`Ember Relay validation failed:\n- ${failures.join('\n- ')}`);
  process.exit(1);
}

console.log(`Ember Relay validated: ${ids.length} unique IDs, ${skillCards} skills, ${localReferences.length} local references, no remote runtime dependencies.`);
