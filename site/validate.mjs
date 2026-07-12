import { readFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(resolve(here, 'index.html'), 'utf8');
const script = readFileSync(resolve(here, 'script.js'), 'utf8');
const failures = [];

const localReferences = [...html.matchAll(/(?:href|src)="([^"]+)"/g)]
  .map((match) => match[1])
  .filter((reference) => !reference.startsWith('#') && !reference.startsWith('http'));

for (const reference of localReferences) {
  if (!existsSync(resolve(here, reference))) failures.push(`Missing local asset: ${reference}`);
}

const ids = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]));
for (const target of [...html.matchAll(/href="#([^"]+)"/g)].map((match) => match[1])) {
  if (!ids.has(target)) failures.push(`Missing fragment target: #${target}`);
}

const expectedSkills = [
  'domain-intel', 'fast-transcript', 'mdk-agent-wallet', 'mdk-l402-api', 'mdk-mcp',
  'mdk-nextjs-checkout', 'mdk-replit-checkout', 'mo-ux-vibedesign-btc', 'nostr-cli',
  'p2p-transfer-filepizza', 'rampart-hook-configurator', 'signal-cli', 'skillspector',
  'timelock-sh', 'wayback-archive',
];

for (const skill of expectedSkills) {
  if (!script.includes(`name: '${skill}'`)) failures.push(`Missing skill entry: ${skill}`);
}

for (const landmark of ['<header', '<nav', '<main', '<footer']) {
  if (!html.includes(landmark)) failures.push(`Missing landmark: ${landmark}>`);
}

if (!html.includes('prefers-reduced-motion') && !readFileSync(resolve(here, 'styles.css'), 'utf8').includes('prefers-reduced-motion')) {
  failures.push('Missing reduced-motion treatment');
}

if (failures.length) {
  console.error(failures.join('\n'));
  process.exit(1);
}

console.log(`Site validation passed: ${localReferences.length} local assets, ${ids.size} fragment targets, ${expectedSkills.length} skills.`);
