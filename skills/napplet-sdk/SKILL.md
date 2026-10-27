---
name: napplet-sdk
description: Reference current `@napplet/sdk` calls from its shipped package domains, OUTBOX-first reads and publishes, social NAPs, relay as an explicit escape hatch, storage, read-only identity, resource bytes, theme, and optional-domain handling. Load the sections needed while implementing; napplet-build owns the project workflow.
compatibility: CLI workflows assume `@napplet/cli` 0.13.0; package versions are independent, so verify installed SDK types.
license: MIT
metadata:
  version: "0.2.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
  upstream_sha: "6c4dafd20142cade5a51ae049beecfef7c8f7c2e"
  upstream_cli: "0.13.0"
  upstream_sdk: "0.30.0"
  upstream_source: "https://github.com/napplet/web/tree/6c4dafd20142cade5a51ae049beecfef7c8f7c2e/skills/napplet-sdk"
---

# @napplet/sdk Reference For Napplet Code

Napplet implementation code is **SDK-first**: import typed wrappers from `@napplet/sdk` for every call. The runtime injects `window.napplet` before module code runs; use `window.napplet?.<domain>` only to decide whether an optional feature renders. Do not hand-build domain clients, envelope dispatchers, or a `window.napplet` object, and do not import `@napplet/shim` in napplet code. Protocol truth: NIP-5D (<https://github.com/nostr-protocol/nips/pull/2303>) and the NAPs track (<https://github.com/napplet/naps>).

## Domains shipped by the current packages

`shell`, `relay`, `identity`, `storage`, `inc`, `theme`, `media`, `notify`, `resource`, `cvm`, `outbox`, `upload`, `intent`, `ble`, `webrtc`, `link`, `count`, `lists`, `serial`, `fs`, `common`, `dm`.

`ifc` is a deprecated INC alias. If a NAP is not in this list, do not implement against it even when a spec PR exists — flag the package/spec gap. `shell` is optional environment information only (see below); there is no `discoverServices()` or `hasService()`, and no domain waits on `shell.ready()`. A missing optional domain simply means "unavailable for this load".

| Need | Domain |
| --- | --- |
| Read/publish Nostr events where relay choice affects correctness | `outbox` |
| Profile lookup, follow/unfollow, reactions, reports, NIP-19 helpers | `common` |
| Safe NIP-51 / NIP-65 list mutations | `lists` |
| Reaction / reply / repost / quote / report / follower counts | `count` |
| Direct messages: send, history, live delivery | `dm` |
| Current shell user pubkey and public snapshots | `identity` (read-only) |
| Persist app state | `storage` |
| External bytes (images, avatars, JSON, WASM side files, media) | `resource` |
| Shell-mediated upload of user files/blobs | `upload` |
| Open an external URL under shell policy | `link` |
| Talk to other napplets | `inc`, `intent` (see `napplet-interop`) |
| Match host colors/fonts | `theme` |
| Playback / now-playing / media commands | `media` |
| Notifications, badges, notification actions | `notify` |
| ContextVM / MCP-style native bridge | `cvm` |
| Bluetooth LE, serial ports, WebRTC signaling, virtual filesystem | `ble`, `serial`, `webrtc`, `fs` |
| One explicit relay, relay diagnostics, protocols outside the outbox model | `relay` (escape hatch only) |

## Optional-domain availability

```ts
import { resource } from '@napplet/sdk';

if (window.napplet?.resource) {
  renderAvatar(await resource.bytes(avatarUrl));
} else {
  renderInitials();
}
```

Disable or hide only that enhancement; never turn one missing optional domain into a broken app. Hard requirements go in the manifest `requires` list as bare domain names; do not duplicate that load gate in app code.

## Outbox — reads and publishes (default for social data)

The napplet supplies filters, IDs, templates, and intent; the shell owns NIP-65 relay discovery, fallbacks, dedup, signature validation, signing, and fanout. `outbox.query` is one-shot; `outbox.subscribe` streams until `sub.close()`. Results are `RelayEventResult` records — the raw event is `result.event`.

```ts
import { outbox, identity } from '@napplet/sdk';

const me = await identity.getPublicKey();           // "" when signed out

const { events } = await outbox.query(
  [{ kinds: [1], authors: [me], limit: 20 }],
  { authors: [me], timeoutMs: 3000 },
);
for (const r of events) renderNote(r.event, r.sidecar?.relayHints);

const sub = outbox.subscribe([{ kinds: [1], authors: [me], limit: 20 }], { authors: [me], timeoutMs: 3000 });
sub.on('event', (r) => renderNote(r.event, r.sidecar?.relayHints));
sub.on('closed', (reason) => markStreamClosed(reason));
sub.close();                                          // on teardown

const result = await outbox.publish({ kind: 1, content: 'hi', tags: [], created_at: Math.floor(Date.now() / 1000) });
if (!result.ok || !result.event) throw new Error(result.error ?? 'publish failed');

await outbox.publish(template, { toInboxes: [recipientPubkey] });   // directed events
```

Current option fields only: `outbox.getEvent` → `author`, `relays`, `timeoutMs`; `outbox.query` / `outbox.subscribe` → `authors`, `relays`, `limit`, `timeoutMs`; `outbox.publish` → `relays`, `toOutbox` (default true), `toInboxes`. There is no `strategy`, no subscribe `live`, no publish `timeoutMs`, no `outbox.eose`.

## Social NAPs — call the NAP that owns the intent

```ts
import { common, lists, count, dm } from '@napplet/sdk';

const profile = await common.getProfile('npub1...');
await common.react(noteId, '+');
await common.follow('npub1...');
await lists.add({ type: 'mute-list' }, [{ itemType: 'pubkey', value: pubkey }]);
const reactions = await count.query({ kinds: [7], '#e': [noteId] });
const status = await dm.status();
if (status.available) await dm.send({ recipients: [pubkey], content: 'hi' });
```

Consent, read-modify-write merges, encryption, signing, routing, and policy stay in the shell. Do not hand-build kind 3 / 7 / 1984 / 10000 events and publish them yourself.

## Relay — explicit escape hatch

Only for relay-local semantics that outbox / common / lists / count / dm cannot express (a specific group relay, raw diagnostics, a protocol outside the outbox model). The design spec must name the reason.

```ts
import { relay } from '@napplet/sdk';

const sub = relay.subscribe(
  [{ kinds: [9, 10, 11, 12], limit: 50 }],
  (r) => renderGroupEvent(r.event),
  () => markCaughtUp(),
  { relay: 'wss://groups.example.com' },
);
sub.close();
```

`relay.publish` is never the default social publish path.

## Storage — scoped, async, 512 KB

```ts
import { storage } from '@napplet/sdk';

await storage.setItem('settings', JSON.stringify({ density: 'compact' }));
const raw = await storage.getItem('settings');      // string | null
await storage.removeItem('settings');
const keys = await storage.keys();                  // string[]
```

`storage.instance.*` is the same surface scoped to this placement (per NAP-STORAGE). `localStorage` / `sessionStorage` / IndexedDB / cookies are unavailable in the sandbox — never reference them.

## Identity — read-only

```ts
import { identity } from '@napplet/sdk';

const me = await identity.getPublicKey();            // hex, or "" when signed out
const sub = identity.onChanged((pubkey) => (pubkey ? loadProfile(pubkey) : showSignedOut()));
sub.close();
```

Also: `getProfile()`, `getFollows()`, `getList(type)`, `getRelays()`, `getMutes()`, `getBlocked()`, `getBadges()`, `getZaps()`. No sign / encrypt / decrypt; `window.nostr` does not exist. Subscribe, do not poll.

## Resource — every external byte

```ts
import { resource } from '@napplet/sdk';

const blob = await resource.bytes('https://example.com/avatar.png');
img.src = URL.createObjectURL(blob);                 // revokeObjectURL when done

const handle = resource.bytesAsObjectURL('blossom:<sha256>.<ext>');
img.src = handle.url;                                // resolves once fetched
handle.revoke();
```

Schemes: `data:` (decoded in-shim), `https:` (shell network under policy), `blossom:<sha256>.<ext>` ([BUD-10](https://github.com/hzrd149/blossom/blob/master/buds/10.md), hash-verified), `htree:` (Hashtree-verified), `nostr:<bech32>` (single-hop NIP-19). Cancel with `bytes(url, { signal })`. Rejections carry a `code` — branch on it, not the message: `not-found`, `blocked-by-policy`, `timeout`, `too-large`, `unsupported-scheme`, `decode-failed`, `network-error`, `quota-exceeded`. The shell byte-sniffs the MIME; never trust upstream `Content-Type`. SVG is rasterized before delivery. `resource.bytesMany` batches.

## Theme

```ts
import { themeGet, themeOnChanged } from '@napplet/sdk';

if (window.napplet?.theme) {
  themeGet().then(applyTheme);
  themeOnChanged(applyTheme);
}
```

`Theme.colors` = `{ background, text, primary }` plus optional `fonts` / `background` / `title`. Whole-surface application rules live in `napplet-ui`.

## Other implemented domains

| Domain | Use when |
| --- | --- |
| `upload` | Shell-mediated file/blob upload |
| `link` | Ask the shell to open an external URL |
| `media` | The napplet owns playback / now-playing or handles media commands |
| `notify` | Shell-rendered notifications, badges, actions |
| `cvm` | Shell-mediated ContextVM / MCP bridge |
| `ble`, `serial` | Bluetooth LE / serial access under shell policy |
| `fs` | Virtual filesystem: selection, metadata, byte reads/writes, directories, change watching |
| `webrtc` | Shell-mediated WebRTC signaling / session setup |

Use the exact method names exported by the installed `@napplet/sdk` version (`node_modules/@napplet/sdk/dist/index.d.ts` is the source of truth for signatures); do not guess parameters from these examples.

## Pitfalls

- `publish()` / `query()` are async; `await` them and check structured results (`ok`, `error`).
- Direct `window.napplet.<domain>.method()` calls when the SDK exports that domain — wrong default.
- `fetch`, `XMLHttpRequest`, `WebSocket`, `<img src="https://…">`, `localStorage`, `window.nostr` — none exist for a napplet; route through `resource`, `storage`, `outbox`.
- There is no `nappletState` / `nappStorage` import — storage is `storage.*`.

## Optional shell environment

`shell` exposes optional environment information through `supports`, `services`, `ready`, and `onReady`. Check injected domain presence for availability; other domains remain usable without waiting for the environment. See [NAP-SHELL](https://github.com/napplet/naps/blob/master/naps/NAP-SHELL.md).

Theme updates reach napplets with the exposed `theme` domain, independently of manifest requirement declarations. User identity changes report the connected signer, including an empty string at sign-out; they do not alter napplet identity. Profile picture/banner bytes use optional `resource` when exposed; otherwise show local placeholder artwork. Theme media URLs do not grant network access, so colors and local fonts provide the fallback. See [NAP-THEME](https://github.com/napplet/naps/blob/master/naps/NAP-THEME.md) and [NAP-IDENTITY](https://github.com/napplet/naps/blob/master/naps/NAP-IDENTITY.md).
