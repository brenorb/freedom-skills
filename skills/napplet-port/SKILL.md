---
name: napplet-port
description: Use when converting an existing Nostr web app, client, or widget into a napplet - inventory the app-owned relay, signing, storage, network, media, shortcut, and routing layers, map each feature to the shipped NAP boundary (OUTBOX-first, relay as escape hatch), split monoliths into focused applets, strip the website chrome, and hand a clean inventory to napplet-design / napplet-build. Run before napplet-design when the starting point is existing code.
compatibility: CLI workflows assume `@napplet/cli` 0.13.0; package versions are independent, so verify installed SDK types.
license: MIT
metadata:
  version: "0.2.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
  upstream_sha: "6c4dafd20142cade5a51ae049beecfef7c8f7c2e"
  upstream_cli: "0.13.0"
  upstream_sdk: "0.30.0"
  upstream_source: "https://github.com/napplet/web/tree/6c4dafd20142cade5a51ae049beecfef7c8f7c2e/skills/napplet-port"
---

# Porting a Nostr App to a Napplet

Run before `napplet-design` when the starting point is an existing app. Do not copy the app architecture into the iframe: a napplet is sandboxed UI plus intent, and the shell owns keys, signing, encryption, relay routing, storage, network bytes, policy — and the window chrome. Protocol truth: NIP-5D (<https://github.com/nostr-protocol/nips/pull/2303>) and the NAPs (<https://github.com/napplet/naps>). Undefined surface is a gap to flag, not something to recreate.

Use only domains the current `@napplet/sdk` exports (list and signatures in `napplet-sdk`). If a NAP is not exported, do not treat it as usable API; list the feature as blocked/deferred. Replace app infrastructure with SDK imports, not hand-written `window.napplet.<domain>` clients; keep `window.napplet?.domain` for optional-domain gating only. If the source app had an async service-discovery layer, remove it — optional shell readiness does not gate the other exposed domains.

## Sandbox authority contract

A port is not complete while any of these remain in napplet runtime code:

- `fetch`, `XMLHttpRequest`, `WebSocket`, relay pools, NIP-65 resolvers, app-owned fanout / dedup.
- `localStorage`, `sessionStorage`, IndexedDB, cookies, browser caches, ad hoc persistence.
- External `<script src>`, `<link href>`, `<img src>`, `<audio|video src>`, CSS network URLs, dynamic network imports.
- `window.nostr`, private keys, local signing, local encryption, signer-extension assumptions.

For asset-heavy ports, inventory every image, font, media file, WASM side file, ROM, and JSON fetch: bundle immutable bytes into the single-file artifact or route them through `resource.bytes` / `resource.bytesMany`. If a dependency cannot run without direct fetch/storage/socket authority, stop and flag it.

## Migration map

| Existing app code | Napplet boundary |
| --- | --- |
| Relay pools, NIP-65 resolution, ranking, fanout, dedup, validation | `outbox` |
| One explicit relay, group relay, diagnostics, protocols outside the outbox model | `relay` (named escape hatch) |
| `window.nostr`, private keys, nostr-tools signing, NIP-07 assumptions | Shell-mediated publish/action NAPs (`outbox`, `common`, `lists`, `dm`) |
| Follow / unfollow / react / report / profile lookup / NIP-19 | `common` |
| NIP-51 / NIP-65 list read-modify-write | `lists` |
| Reaction / reply / repost / quote / report / follower counts | `count` |
| DM protocol, message store, encryption, key sessions | `dm` |
| `localStorage`, IndexedDB, cookies | `storage` |
| `fetch`, XHR, WebSocket, direct external images/media | `resource`, `upload`, `link`, `media` |
| App-level cross-window / plugin bus | `inc`, `intent` (`napplet-interop`) |
| Keyboard interactions | Ordinary buttons and browser input controls |
| Notifications, badges | `notify` |
| Device / native bridges | `ble`, `serial`, `webrtc`, `cvm`, `fs` only when the shipped domain fits |
| App header, logo, nav bar, footer, marketing sections, page router | **Delete.** The runtime frames the applet and shows its name; each focused napplet is one screen (`napplet-ui`) |
| Fixed desktop layout / min-widths / centered max-width column | Compact, full-frame, tiered layout (`napplet-ui`) |


If a relay client, signer, direct storage layer, direct network layer, or site chrome survives this pass, assume the boundary is wrong until proven otherwise.

## Step 1 — Inventory

```
feature | existing code path | direct authority today | replacement NAP | hard/optional | notes
feed reads | RelayPool.subscribe + NIP-65 | relay routing | outbox | hard | author write relays matter
post note | signer.sign + relay.publish | signing + fanout | outbox.publish | hard | toInboxes for directed posts
react | build kind 7 + sign + publish | social action | common.react | optional | hide action when absent
mute | edit kind 10000 | list mutation | lists.add | optional | shell preserves list state
avatar | fetch(url) | network bytes | resource.bytes | optional | object URL + revoke
site header/nav | Header.tsx | — | delete | — | runtime shows the name
```

## Step 2 — Split the monolith

| App area | Likely napplet |
| --- | --- |
| Home / feed | feed viewer |
| Composer | note composer |
| Profile page / editor | profile viewer / editor |
| Notifications | notification viewer |
| DMs | DM client |
| Relay / admin tools | relay diagnostics or manager |

Hand off between napplets with `inc` / `intent`. Do not rebuild the monolith with tabs unless the prompt explicitly wants one compound napplet and it still works in a small frame.

## Step 3 — Rewrite data access

```ts
import { outbox, common, lists, count, dm, storage, resource } from '@napplet/sdk';

const { events } = await outbox.query([{ authors: [author], kinds: [1], limit: 20 }], { authors: [author], timeoutMs: 3000 });
const sub = outbox.subscribe([{ kinds: [1], authors: [author], limit: 50 }], { authors: [author], timeoutMs: 3000 });
sub.on('event', (r) => render(r.event, r.sidecar?.relayHints));

const published = await outbox.publish({ kind: 1, content, tags, created_at: Math.floor(Date.now() / 1000) });
if (!published.ok) showPublishError(published.error);

await common.react(noteId, '+');
await lists.add({ type: 'mute-list' }, [{ itemType: 'pubkey', value: pubkey }]);
const totals = await count.query({ kinds: [7], '#e': [noteId] });
await dm.send({ recipients: [pubkey], content: 'hello' });
```

Keep `relay` only where the inventory says "explicit relay-local escape hatch" and names the reason.

## Step 4 — Remove forbidden surfaces

Search and delete or replace: `window.nostr`, key material, `signEvent`, `nip04`, `nip44`; `new WebSocket("wss://…")`, pool libraries, NIP-65 resolvers; `fetch`, `XMLHttpRequest`, external `<img src>`, external scripts/styles; `localStorage`, `sessionStorage`, IndexedDB, cookies; `discoverServices`, `hasService`, and any startup gate on `shell.ready()` / `shell.supports()`. Optional-domain gating is a property check after injection:

```ts
if (window.napplet?.common) enableSocialActions(); else disableSocialActions();
```

## Step 5 — Hand off

```
nappletType:
source app:
features kept:
features split / deferred:
NAPs used:
package / proposal gaps:
requires (hard only):
optional domains and fallbacks:
SDK imports:
outbox reads / publishes:
social / list / count / dm actions:
media / notify / device domains:
relay escape hatches (with reasons):
storage keys:
resource URLs / schemes:
removed app-owned infrastructure:
removed site chrome (header/nav/footer/router):
form factor: compact; tiers; minimum (if any)
verification scenarios:
```

The stop condition is not "the old app compiles". It is "the napplet no longer owns authority that belongs to the shell, has no website chrome, and every feature maps to a current NIP-5D / NAP / package surface".
