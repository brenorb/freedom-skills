// In-memory loopback relay for real CLI tests; never connects to other relays.
// It retains accepted bytes for inspection. Ephemeral non-retention is tested
// separately by the E2E benchmark's services.mjs fixture.
import { createServer } from 'node:http';
import { createRequire } from 'node:module';
import { existsSync, realpathSync } from 'node:fs';
import { delimiter, join } from 'node:path';

// Reuse the tested CLI's ws dependency, including installations via npm's .bin.
const entrypoint = process.argv[2] && process.argv[2] !== '--reject'
  ? process.argv[2]
  : process.env.PATH.split(delimiter).map(dir => join(dir, 'nowhere')).find(existsSync);
if (!entrypoint) throw new Error('Run this fixture in the npx nowhere-cli environment or pass the CLI entrypoint.');
const require = createRequire(realpathSync(entrypoint));
const { WebSocketServer } = require('ws');
const { verifyEvent } = require('nostr-tools/pure');
const rejectWrites = process.argv.includes('--reject');
const events = new Map();

function matches(event, filter) {
  if (filter.ids && !filter.ids.some(id => event.id.startsWith(id))) return false;
  if (filter.authors && !filter.authors.some(key => event.pubkey.startsWith(key))) return false;
  if (filter.kinds && !filter.kinds.includes(event.kind)) return false;
  if (filter.since !== undefined && event.created_at < filter.since) return false;
  if (filter.until !== undefined && event.created_at > filter.until) return false;
  return Object.entries(filter).every(([key, values]) => !key.startsWith('#') ||
    event.tags.some(tag => tag[0] === key.slice(1) && values.includes(tag[1])));
}

const server = createServer((request, response) => {
  if (request.url !== '/events') {
    response.writeHead(404).end();
    return;
  }
  response.writeHead(200, { 'Content-Type': 'application/json' });
  response.end(JSON.stringify([...events.values()]));
});
const sockets = new WebSocketServer({ server });
sockets.on('connection', socket => {
  socket.on('message', raw => {
    const [kind, id, ...filters] = JSON.parse(raw.toString());
    if (kind === 'EVENT') {
      const event = id;
      const accepted = !rejectWrites && verifyEvent(event);
      if (accepted) events.set(event.id, event);
      socket.send(JSON.stringify(['OK', event.id, accepted, accepted ? '' : 'blocked: test rejection or invalid signature']));
    } else if (kind === 'REQ' || kind === 'COUNT') {
      const found = [...events.values()].filter(event => filters.some(filter => matches(event, filter)));
      if (kind === 'COUNT') {
        socket.send(JSON.stringify(['COUNT', id, { count: found.length }]));
      } else {
        for (const event of found) socket.send(JSON.stringify(['EVENT', id, event]));
        socket.send(JSON.stringify(['EOSE', id]));
      }
    }
  });
});
server.listen(0, '127.0.0.1', () => {
  process.stdout.write(JSON.stringify({ url: `ws://127.0.0.1:${server.address().port}` }) + '\n');
});
