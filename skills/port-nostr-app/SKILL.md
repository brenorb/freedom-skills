---
name: port-nostr-app
description: Use when converting an existing Nostr web app into a napplet - audit app-owned relay, signing, storage, network, media, keyboard shortcuts, and routing layers; map each feature to a current package-implemented NAP boundary; default social reads and publishes to NAP-OUTBOX, not NAP-RELAY; then hand a clean build spec to design-napplet/build-napplet.
metadata:
  version: "0.1.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
---

# Porting A Nostr App To A Napplet

Use this before `design-napplet` when the starting point is an existing Nostr app. Do not copy the app architecture into the iframe. A napplet is sandboxed UI plus intent; the shell owns keys, signing, encryption, relay routing, storage, network bytes, and policy.

Protocol truth: NIP-5D (<https://github.com/nostr-protocol/nips/pull/2303>) plus NAPs (<https://github.com/napplet/naps>). Open the canonical spec before adding or depending on any message type, manifest tag, capability, or loading rule. If a needed surface is undefined, flag the gap instead of inventing it.

Use current package exports as the implementation boundary. Implemented package
domains are `relay`, `identity`, `storage`, `inc`, `theme`, `keys`, `media`,
`notify`, `config`, `resource`, `cvm`, `outbox`, `upload`, `intent`, `ble`,
`webrtc`, `link`, `count`, `lists`, `serial`, `fs`, `common`, and `dm`. If a NAP is
not exported by the current `@napplet/*` packages, do not treat it as usable API.
Map a need to an existing shipped NAP only when it faithfully owns the intent;
otherwise list the feature as blocked/deferred.

Ports should replace app-owned infrastructure with `@napplet/sdk` imports, not
with hand-written `window.napplet.<domain>.*` clients. Keep direct
`window.napplet?.domain` access for post-injection optional-domain fallback
checks; use SDK helper exports for actual calls whenever they exist.

Current packages do not expose `window.napplet.shell`, `shell.ready()`, or
`shell.supports(...)`. Use `@napplet/sdk` wrappers for calls and use
`window.napplet?.domain` only as an optional-domain fallback check after runtime
injection. If a source app needed an async service-discovery layer, remove that
layer or flag the missing package/runtime surface instead of recreating it
inside the napplet.

## Sandbox Authority Contract

Do not preserve browser authority from the source app. A port is not complete
until these surfaces are gone from napplet runtime code:

- `fetch`, `XMLHttpRequest`, `WebSocket`, relay pools, direct NIP-65 routing, and
  any app-owned network fanout.
- `localStorage`, `sessionStorage`, IndexedDB, cookies, filesystem-like browser
  caches, and ad hoc persistence.
- External `<script src>`, `<link href>`, `<img src>`, `<audio src>`,
  `<video src>`, CSS network URLs, and dynamic network imports.
- `window.nostr`, raw private keys, local signing, local encryption/decryption,
  or extension-specific signer assumptions.

For resource-heavy ports, inventory every ROM, WASM side file, avatar, image,
font, media file, and JSON fetch. Bundle immutable bytes into the single-file
artifact when that is the product shape; otherwise route them through
`resource.bytes` / `resource.bytesMany`. If the old dependency cannot run
without direct browser fetch/storage/socket authority, stop and flag that
dependency instead of wrapping it in a napplet.

## Migration Rule

Replace app-owned infrastructure with the highest-level NAP that owns the user intent:

| Existing app code | Napplet boundary |
| --- | --- |
| Relay pools, NIP-65 outbox resolution, relay ranking, fanout, dedup, event validation | `outbox` |
| One explicit relay, group relay, raw relay diagnostics, protocol tooling outside the outbox model | `relay` |
| `window.nostr`, private keys, nostr-tools signing, NIP-07 assumptions | Shell-mediated publish/action NAPs (`outbox`, `common`, `lists`, `dm`) |
| Follow/unfollow/react/report/profile lookup/NIP-19 helpers | `common` |
| NIP-51/NIP-65 list read-modify-write | `lists` |
| Reaction/reply/repost/quote/report/follower counts | `count` |
| DM protocol, message storage, encryption, key sessions, relay routing | `dm` |
| `localStorage`, IndexedDB, cookies | `storage` |
| `fetch`, `XMLHttpRequest`, WebSocket, direct external images/media | `resource`, `upload`, `link`, `media`, or shell-owned NAPs |
| App-level cross-window/plugin bus | `inc` or `intent` |
| Global shortcuts, editor hotkeys, action keybindings | `keys` |
| Notifications, badges, notification actions | `notify` |
| Device/native session bridges | `ble`, `serial`, `webrtc`, or `cvm` only when the current package domain fits |
| File browsing, directory listing, byte reads/writes, change watching | `fs` — shell-mediated virtual filesystem access |

If the port still contains a relay client, signer, direct storage layer, or direct network layer after this pass, assume the boundary is wrong until proven otherwise.

Do not add `keys` to `requires` when local buttons, menus, text input, or
click/tap controls let the napplet function without shell-managed key
reservation. Treat key reservation as optional unless the port's core workflow
cannot work without shell-owned reserved shortcuts.

## Step 1 - Inventory The Existing App

Make a table before editing:

```
feature | existing code path | current direct authority | replacement NAP | hard/optional | notes
feed reads | RelayPool.subscribe + NIP-65 | relay routing | outbox | hard | author write relays matter
post note | signer.sign + relay.publish | signing + fanout | outbox.publish | hard | toInboxes for directed posts
react | build kind 7 + signer + relay | social action | common.react | optional | fallback disables action
mute pubkey | edit kind 10000 | list mutation | lists.add | optional | preserve list state shell-side
avatar | fetch(url) | network bytes | resource.bytes | optional | object URL + revoke
```

Use this table as the design spec input. Do not start by wiring compatibility shims around the old app services.

## Step 2 - Split Monoliths Into Napplets

NIP-5D napplets should be small and focused. A full Nostr app usually becomes several napplets:

| App area | Likely napplet |
| --- | --- |
| Home/feed timeline | feed viewer |
| Composer | note composer |
| Profile page/editor | profile viewer/editor |
| Notifications | notification viewer |
| Direct messages | DM client |
| Relay/admin tools | relay diagnostic or relay manager |

Use `inc` or `intent` for handoff between napplets. Do not recreate the monolith with tabs unless the prompt explicitly asks for a single compound app and the shell context supports that shape.

## Step 3 - Rewrite Data Access

Default patterns:

```ts
import { outbox, common, lists, count, dm, storage, resource } from '@napplet/sdk';

const { events } = await outbox.query(
  [{ authors: [author], kinds: [1], limit: 20 }],
  { authors: [author], timeoutMs: 3000 },
);

const sub = outbox.subscribe([{ kinds: [1], authors: [author], limit: 50 }], {
  authors: [author],
  timeoutMs: 3000,
});
sub.on('event', (result) => render(result.event, result.sidecar?.relayHints));

const publish = await outbox.publish({
  kind: 1,
  content,
  tags,
  created_at: Math.floor(Date.now() / 1000),
});
if (!publish.ok) showPublishError(publish.error);

await common.react(noteId, '+');
await lists.add({ type: 'mute-list' }, [{ itemType: 'pubkey', value: pubkey }]);
const totals = await count.query({ kinds: [7], '#e': [noteId] });
await dm.send({ recipients: [pubkey], content: 'hello' });
```

Only keep `relay` when the inventory table says "explicit relay-local escape hatch" and names the reason.

## Step 4 - Remove Forbidden Surfaces

Search and delete or replace:

- `window.nostr`, private key material, `signEvent`, `nip04`, `nip44`, local encryption/session keys.
- `new WebSocket("wss://...")`, relay pool libraries, direct NIP-65 resolvers, app-owned fanout/dedup.
- `fetch`, `XMLHttpRequest`, direct `<img src="https://...">`, external scripts/styles.
- `localStorage`, `sessionStorage`, IndexedDB, cookies.
- Generic capability probes such as `discoverServices`, `hasService`,
  `shell.ready()`, or `shell.supports(...)`.

Optional-domain fallback checks are property checks after runtime injection; use
SDK imports for the actual calls inside enabled branches:

```ts
if (window.napplet?.common) enableSocialActions();
else disableSocialActions();
```

## Step 5 - Hand Off To Build

Produce this handoff for `design-napplet` / `build-napplet`:

```
nappletType:
source app:
features kept:
features split/deferred:
NAPs used:
package/proposal gaps:
requires:
optional domains and fallbacks:
SDK helpers/imports:
outbox reads:
outbox publishes:
social/list/count/dm actions:
keys/media/notify/device domains:
relay escape hatches:
storage keys:
resource URLs/schemes:
removed app-owned infrastructure:
verification scenarios:
```

The stop condition for this skill is not "the old app compiles." It is "the napplet no longer owns authority that belongs to the shell, and every feature maps to a current NIP-5D/NAP/package surface."
