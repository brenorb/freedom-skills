---
name: build-napplet
description: Use when writing a napplet (sandboxed Nostr iframe app) - Vite setup, the NIP-5A manifest plugin, runtime-injected window.napplet, the @napplet/sdk API for every current package-implemented NAP domain, OUTBOX-first event access, relay as explicit escape hatch, optional NAP-KEYS shortcuts/keybindings, post-injection optional-domain fallback checks, and the single-file artifact rule. Pairs with design-napplet (plan first), port-nostr-app (for migrations), and test-napplet (verify before publish).
metadata:
  version: "0.1.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
---

# Building a Napplet

Implements a `design-napplet` spec. A napplet is a single self-contained `/index.html` the shell loads into a `sandbox="allow-scripts"` iframe (no `allow-same-origin`); all host access is proxied over postMessage per NIP-5D. The napplet never holds keys. Protocol truth: NIP-5D (<https://github.com/nostr-protocol/nips/pull/2303>) + NAPs (<https://github.com/napplet/naps>). Never invent wire surface; flag gaps.

## Sandbox Authority Contract

Treat this as a pre-code gate. If the implementation plan needs any direct
browser network, browser persistence, or external runtime asset, rewrite the
plan before coding.

- Never call `fetch`, `XMLHttpRequest`, `WebSocket`, `localStorage`,
  `sessionStorage`, IndexedDB, `document.cookie`, `window.nostr`, or any relay
  pool/signing API from napplet code.
- Never load runtime bytes through external `<script src>`, `<link href>`,
  `<img src>`, `<audio src>`, `<video src>`, CSS `url(https://...)`, dynamic
  `import("https://...")`, or side files that the opaque-origin `srcdoc`
  iframe must fetch.
- ROMs, WASM companions, images, avatars, media, fonts, JSON, and other bytes
  must be either folded into the single `/index.html` artifact at build time or
  requested through `resource.bytes` / `resource.bytesMany` under shell policy.
- Browser-local state must use `storage`; Nostr network reads/publishes must use
  `outbox`, `common`, `lists`, `count`, `dm`, or a documented `relay` escape
  hatch; external URL opening must use `link`.
- If a dependency contains dormant forbidden references, prove they are removed,
  tree-shaken, or replaced by NAP-backed adapters in the built output. If a
  dependency actually needs direct fetch/storage/socket authority at runtime,
  stop and flag it instead of shipping.

Use only domains and helpers shipped by the current packages. Current package
domains are:

`relay`, `identity`, `storage`, `inc`, `theme`, `keys`, `media`, `notify`,
`config`, `resource`, `cvm`, `outbox`, `upload`, `intent`, `ble`, `webrtc`,
`link`, `count`, `lists`, `serial`, `fs`, `common`, and `dm`.

The deprecated `ifc` subpath is only an INC compatibility alias; new napplets use
`inc`. If a NAP is not in the list above, do not implement against it as usable
API even if a spec PR exists. Flag the package/spec gap.

## Runtime Injection And SDK

The runtime injects `window.napplet` before napplet scripts run. Napplet code
does not import `@napplet/shim`; runtimes consume that package when they need the
first-party installer. Current packages do not expose `window.napplet.shell`,
`shell.ready()`, or `shell.supports(...)`; do not add a napplet-owned readiness
handshake, generic capability probe, or synthetic shell namespace. A missing
optional domain means "feature unavailable for this load"; a missing hard
requirement belongs to the manifest load gate.

Napplet implementation code is **SDK-first**. Use `@napplet/sdk` wrappers for
calls: import named, typed wrappers from `@napplet/sdk` for every domain call
the SDK exposes. Use direct `window.napplet?.domain` access only for optional
domain fallback checks after runtime injection, or for a real package gap where
no SDK wrapper exists.

Canonical pattern:

```ts
import { outbox, common, inc, storage, identity } from '@napplet/sdk';
```

Do not hand-build NAP domain clients, envelope dispatchers, or `window.napplet`
objects inside napplet code. The SDK wrappers still delegate to the injected
runtime at call time, but they keep examples typed, current, and aligned with
the package surface agents actually import.

## Step 1 — Start From The CLI Scaffold

For a new napplet, scaffold and initialize through the primary CLI. `create`
delegates to the canonical `github.com/napplet/boilerplate` template and
preserves the package manager pin, Vite config, single-file build plumbing, scripts,
conformance wiring, docs layout, and starter source structure. `init` owns the
deployment d-tag, title, optional description, and canonical archetype metadata.

```bash
napplet create my-napplet
cd my-napplet
napplet init
```

Do not recreate `package.json`, `pnpm-lock.yaml`, `vite.config.ts`, TypeScript
config, `index.html`, conformance scripts, or release/build plumbing inline.
Agents should edit the generated project, not replace its substrate.

Use the existing-app/manual path only when the user explicitly asks to retrofit
napplet support into a pre-existing app. In that case, mirror the boilerplate's
tooling shape instead of inventing a local one.

## Step 2 — Project-Specific Edit Points

After scaffolding, keep the boilerplate-owned files and make only the
project-specific edits the generator/template expects:

- `package.json`: package name only, plus dependencies only when the feature
  truly needs them.
- `.napplet/config.json`: inspect the CLI-owned deployment metadata; do not
  duplicate it elsewhere.
- `vite.config.ts`: hard `requires` and optional config schema; preserve the
  template d-tag fallback.
- `index.html`: title/root markup that the UI needs.
- `src/main.ts` and `src/styles.css`: application behavior and presentation.
- `README.md` and `docs/*`: project-specific usage, boundaries, and verification
  notes.

Preserve the template scripts unless the project has an explicit reason to
change them:

```jsonc
{
  "scripts": {
    "build": "vite build",
    "type-check": "tsc --noEmit",
    "verify": "pnpm type-check && pnpm build",
    "test:conformance": "pnpm build && napplet-conformance ./dist"
  }
}
```

## Step 3 — Configure build requirements

The boilerplate already wires `nip5aManifest`. Update hard `requires` rather
than replacing the config. `nip5aManifest` hashes build output and writes a
local sidecar. Its required `nappletType` is a build-local fallback; the CLI's
validated `.napplet/config.json` metadata takes precedence during deploy.

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import { nip5aManifest } from '@napplet/vite-plugin';

export default defineConfig({
  plugins: [
    nip5aManifest({
      nappletType: 'my-napplet',     // template fallback; deploy metadata comes from napplet init
      artifactMode: 'single-file',   // fold assets + keep inline scripts in one index.html
      // requires: ['outbox', 'storage'], // hard requirements only; omit optional enhancements
    }),
  ],
});
```

The aggregate hash is computed into the manifest (`.nip5a-manifest.json`) and the signed event — it is **not** injected as a meta tag. Set `VITE_DEV_PRIVKEY_HEX` (hex 32-byte key) to produce a signed manifest in CI; dev builds work without it.

### Describe archetypes with stable conventions

When the napplet fulfills an archetype role, use the current `archetypes` option
and one stable, queryless convention identity per entry. The convention must use
`napplet:<archetype>/<intent>` and its archetype segment must match `slug`.

```ts
archetypes: [
  { slug: 'note', convention: 'napplet:note/open' },
]
```

This emits `["archetype", "note", "napplet:note/open"]`. Never put a query in manifest discovery metadata or invent payload, version, or negotiation fields.

## Step 4 — Read And Publish Nostr Events Through Outbox First

Most napplets should use NAP-OUTBOX for Nostr event reads and publishes. The napplet supplies filters, event IDs, publish templates, and intent; the shell owns NIP-65 relay discovery, fallbacks, relay intelligence, deduplication, signature validation, signing, and fanout policy.

`outbox.query` is a one-shot read. `outbox.subscribe` is a live stream; call `sub.close()` to stop. Event returns are `RelayEventResult` records, so read the raw event at `result.event`.

```ts
import { outbox, identity } from '@napplet/sdk';

const me = await identity.getPublicKey();
if (!me) renderSignedOut();

const { events } = await outbox.query(
  [{ kinds: [1], authors: [me], limit: 20 }],
  { authors: [me], timeoutMs: 3000 },
);
for (const result of events) renderNote(result.event, result.sidecar?.relayHints);

const sub = outbox.subscribe(
  [{ kinds: [1], authors: [me], limit: 20 }],
  { authors: [me], timeoutMs: 3000 },
);
sub.on('event', (result) => renderNote(result.event, result.sidecar?.relayHints));
sub.on('closed', (reason) => markStreamClosed(reason));

sub.close(); // on teardown
```

Publish through `outbox.publish` for normal user-authored social/event output. The shell signs; the napplet never holds keys. Check `ok` because publish failures return structured results.

```ts
import { outbox } from '@napplet/sdk';

const result = await outbox.publish({
  kind: 1,
  content: 'Hello from a napplet!',
  tags: [],
  created_at: Math.floor(Date.now() / 1000),
});
if (!result.ok || !result.event) throw new Error(result.error ?? 'publish failed');
console.log('published', result.event.id);
```

For directed events, pass `toInboxes` so the shell can include recipient inbox relays.
`toOutbox` defaults to true; pass `relays` only for explicit relay URL fanout
candidates subject to shell validation.

```ts
await outbox.publish(template, { toInboxes: [recipientPubkey] });
```

## Step 5 — Use Higher-Level Social NAPs Before Raw Events

When a NAP owns the user intent, call that NAP instead of building and publishing raw events.

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

This keeps consent, read-modify-write merges, list preservation, encryption, signing, relay routing, and policy in the shell.

## Step 6 — Relay Is A Low-Level Escape Hatch

Use NAP-RELAY only when the feature needs relay-local semantics that OUTBOX and higher-level NAPs cannot express: a specific group relay, raw relay diagnostics, relay protocol tools, or a domain-specific protocol outside the outbox model.

```ts
import { relay } from '@napplet/sdk';

const sub = relay.subscribe(
  [{ kinds: [9, 10, 11, 12], limit: 50 }],
  (result) => renderGroupEvent(result.event),
  () => markCaughtUp(),
  { relay: 'wss://groups.example.com' },
);
sub.close();
```

Do not use `relay.publish` as the default social publish path. Prefer `outbox.publish`, `common`, `lists`, or `dm` unless the design spec names the exact relay escape hatch.

## Step 7 — Scoped storage

Storage is async, proxied through the shell, scoped per napplet (512 KB quota). Never touch `localStorage` (throws `SecurityError` without `allow-same-origin`).

```ts
import { storage } from '@napplet/sdk';

await storage.setItem('settings', JSON.stringify({ theme: 'dark' }));
const raw = await storage.getItem('settings');     // string | null
const settings = raw ? JSON.parse(raw) : {};
await storage.removeItem('settings');
const keys = await storage.keys();                 // string[]
```

`storage.instance.*` exposes the same surface scoped to this napplet **instance** (per NAP-STORAGE) when you need per-placement state.

## Step 8 — Read-only identity

`getPublicKey()` always resolves: hex pubkey when a user is connected, `""` when not. Don't poll — subscribe to changes. Identity is strictly read-only (no sign/encrypt/decrypt).

```ts
import { identity } from '@napplet/sdk';

const me = await identity.getPublicKey();          // "" when signed out
const sub = identity.onChanged((pubkey) => {
  pubkey ? loadProfile(pubkey) : showSignedOut();
});
sub.close();
```

Also available: `getProfile()`, `getFollows()`, `getList(type)`, `getRelays()`, `getMutes()`, `getBlocked()`, `getBadges()`, `getZaps()`. Use `common` for profile lookup and social actions when available; `identity` is for the current shell user snapshot.

## Step 9 — Inter-napplet events and intents

`inc.emit` broadcasts to topic subscribers; `inc.on` receives one `IncEvent`
containing the exact topic, runtime-attested sender, and optional payload. Use exact,
opaque convention topics such as `napplet:note/open`, `napplet:profile/open`,
or `napplet:dm/open`. A topic is an identifier, not a payload schema.

```ts
import { inc } from '@napplet/sdk';

inc.emit('napplet:profile/open?pubkey=abc123');
// Runtime emits { type: 'inc.emit', topic: 'napplet:profile/open', payload: { pubkey: 'abc123' } }.

const sub = inc.on('napplet:profile/open', (event) => {
  if (!isValidProfileOpenPayload(event.payload)) return;
  openProfile(event.payload);
});
sub.close();
```

NAP-INC `emit(topic, payload?)` may use a queried convention URI. The runtime
turns its shallow text query into payload and routes the stable queryless topic;
subscribe to that stable queryless topic. Literal `+` stays plus and
percent-decoding applies only to the emitted query text. A fragment, malformed
percent encoding, repeated decoded name, or query plus explicit payload throws
synchronously; use a queryless topic plus explicit payload for structured or
non-text data.

NAP-INTENT dispatches by archetype through `invoke(request)` or
`open(archetype, payload?, opts?)`:

```ts
import { intent } from '@napplet/sdk';

const result = await intent.open(
  'profile',
  { pubkey: 'abc123' },
  { convention: 'napplet:profile/open', behavior: { newWindow: true } },
);
if (!result.handled) showIntentError(result.error);
```

Results contain required `ok`, `archetype`, `action`, and `handled` fields.
Archetype routing and optional convention-based payload interpretation are
orthogonal.

Payload choices remain local to a real upstream convention, so validate every
received value. Subscriptions, manifest discovery, and routing stay exact on the
stable, queryless convention identity: do not parse queries there or add prefix,
wildcard, canonicalization, or multi-convention matching. See the living
[NAP-INC](https://github.com/napplet/naps/blob/master/naps/NAP-INC.md) and
[NAP-INTENT](https://github.com/napplet/naps/blob/master/naps/NAP-INTENT.md)
documents for the normative contract.

## Step 10 — Domain availability

There is **no** `discoverServices()`/`hasService()` and no generic shell
capability query. Current packages do not expose `window.napplet.shell`,
`shell.ready()`, or `shell.supports(...)`. NIP-5D runtimes inject
`window.napplet` before napplet code runs. Available domains are present as
properties; unavailable domains are absent. Use `@napplet/sdk` wrappers for
calls; use direct property checks only to decide whether an optional feature
should render or fall back after the injected namespace exists.

```ts
if (window.napplet?.resource) {
  const blob = await resource.bytes(avatarUrl);
  renderAvatar(blob);
} else {
  renderInitials();
}
```

Do not turn one missing optional domain into a broken app state. Disable or hide
only that enhancement. For hard manifest requirements, do not duplicate the
load gate in app code; the shell should refuse incompatible loads before the app
runs.

## Step 11 — Fetch external bytes (resource NAP)

The sandboxed napplet model does not give app code ambient network authority.
Route every external byte through `resource` instead of `fetch`,
`<img src=https://…>`, `XMLHttpRequest`, or `WebSocket`.

```ts
import { resource } from '@napplet/sdk';

const blob = await resource.bytes('https://example.com/avatar.png');
imgEl.src = URL.createObjectURL(blob);             // revokeObjectURL when done

const handle = resource.bytesAsObjectURL(
  'blossom:sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
);
imgEl.src = handle.url; // resolves once fetched
handle.revoke();        // when done
```

Schemes: `data:` (decoded in-shim, no round-trip), `https:` (shell network under policy), `blossom:sha256:<hex>` (hash-verified), `htree:` (Hashtree-verified), `nostr:<bech32>` (single-hop NIP-19). Cancel with `bytes(url, { signal })`. Rejections carry a `code` — branch on it, never the message string:
`not-found`, `blocked-by-policy`, `timeout`, `too-large`, `unsupported-scheme`, `decode-failed`, `network-error`, `quota-exceeded`.

The shell byte-sniffs and classifies the MIME; never trust the upstream `Content-Type`. SVG inputs are rasterized server-side — napplets never receive `image/svg+xml`.

## Step 12 — Config & theme (optional)

```ts
import { config, themeGet, themeOnChanged } from '@napplet/sdk';

if (window.napplet?.config) {
  await config.registerSchema({
    type: 'object',
    properties: { accent: { type: 'string', default: 'blue' } },
  });
  const cfg = await config.get();
  apply(cfg);
  const cfgSub = config.subscribe((v) => apply(v));
  config.openSettings();
}

const colors = await themeGet();
const themeSub = themeOnChanged((t) => paint(t));
```

### Apply NAP-THEME to the entire surface

Theme support is incomplete if only controls or accent colors change. Use CSS
custom properties and apply the runtime theme to the page background, text,
surfaces, borders, primary color, and muted content. Set the background on
`:root`, `html`, `body`, and the app root when those elements are present so the
host never exposes a browser-white canvas around a dark UI.

```ts
import { themeGet, themeOnChanged, type Theme } from '@napplet/sdk';

function applyTheme(theme: Theme): void {
  const root = document.documentElement;
  const body = document.body;
  root.style.setProperty('--nap-bg', theme.colors.background);
  root.style.setProperty('--nap-fg', theme.colors.text);
  root.style.setProperty('--nap-primary', theme.colors.primary);
  root.style.backgroundColor = theme.colors.background;
  body.style.backgroundColor = theme.colors.background;
  body.style.color = theme.colors.text;
}

if (window.napplet?.theme) {
  themeGet().then(applyTheme);
  themeOnChanged(applyTheme);
} else {
  applyTheme(LOCAL_FALLBACK_THEME); // explicit background, never browser default
}
```

Use the exact `Theme` fields exported by the installed package version. Derive
surface, border, and muted tokens from those documented colors in one local
function when the payload does not expose them. Verify a dark and a light
runtime theme and inspect empty margins and loading/error states too.

NAP-CONFIG defines runtime `config.registerSchema`, but its current proposal does
not define a manifest-tag or HTML-meta encoding for build-time schemas. Do not
treat vite-plugin config metadata as interoperable protocol. Recheck the living
[NAP-CONFIG proposal](https://github.com/napplet/naps/pull/14) before adding
settings. Gate config and theme behind `window.napplet?.config` /
`window.napplet?.theme`.

## Step 12 — Keyboard shortcuts and actions (keys NAP)

If the feature mentions shortcuts, hotkeys, keyboard forwarding, command
palettes, editor actions, media shortcuts, or app-level keybinds, use NAP-KEYS.
Do not hand-roll global key capture as the main integration path; the shell owns
reserved shortcuts and binding policy.

Do not add `keys` to `requires` just because shortcuts would be nice. Treat key
reservation as optional when local buttons, menus, text input, click/tap
controls, or app-local fallback shortcuts let the napplet still perform its core
task.

```ts
import { keys } from '@napplet/sdk';

if (window.napplet?.keys) {
  const saveBinding = await keys.register(
    { id: 'note.save', label: 'Save note', defaultKey: 'Ctrl+S' },
    () => saveCurrentNote(),
  );

  // On teardown:
  saveBinding.close();
}
```

Use stable action IDs (`domain.action` or `feature.action`) so shells can
remember bindings. Always close handles on teardown.

## Step 13 — Other implemented package NAPs

These are implemented package domains too; include them when the feature needs
their exact boundary:

| Domain | Use when |
| --- | --- |
| `upload` | The napplet needs shell-mediated file/blob upload. |
| `link` | The napplet asks the shell to open an external URL. |
| `intent` | The napplet invokes or exposes app-to-app actions. |
| `media` | The napplet owns playback/now-playing state or handles media commands. |
| `notify` | The napplet needs shell-rendered notifications, badges, or actions. |
| `cvm` | The napplet needs a shell-mediated ContextVM/MCP bridge. |
| `ble` | The napplet needs Bluetooth LE/GATT access. |
| `serial` | The napplet needs serial-port access. |
| `fs` | The napplet needs shell-mediated virtual filesystem access, including virtual file selection, metadata, byte reads/writes, directory operations, or change watching. |
| `webrtc` | The napplet needs shell-mediated WebRTC signaling/session setup. |

Use `window.napplet?.domain` only for optional-domain fallback checks after
runtime injection. Declare bare domain names in `requires` only for hard
requirements.

## Runtime Preview With Paja

Runtime injection belongs to the shell. Napplet application code should consume
typed helpers from `@napplet/sdk` for calls and the injected `window.napplet`
namespace for capability checks; do not add napplet-owned bootstrap plumbing.

Do not report the Vite server as the napplet preview. Vite only serves the
artifact; Paja supplies the runtime that injects `window.napplet` and exercises
the shell boundary. From the initialized project, use:

```bash
napplet paja -- pnpm vite --host 127.0.0.1
```

Copy the URL printed by Paja into the completion report. If `napplet` or the
configured Kehto/Paja binary is missing, report that prerequisite and use
conformance for automated verification; do not claim a raw Vite URL can load
the finished napplet.

## Boilerplate Validation

Before claiming done on a generated napplet, run the template's own commands
from the generated project directory:

```bash
pnpm install
pnpm verify
pnpm test:conformance
```

If the user intentionally starts from an existing app instead of the
boilerplate, add equivalent scripts that match the boilerplate contract and run
those exact commands before completion.

## Common pitfalls

- Recreating the boilerplate by hand — **wrong substrate.** Start from
  `@napplet/boilerplate` for new napplets and preserve its scripts/config/layout.
- Napplet-owned `@napplet/shim` bootstrap — **wrong layer.** The runtime injects `window.napplet`; napplets use `@napplet/sdk` for calls and direct domain properties only for post-injection optional-domain fallback checks.
- Reaching straight into `window.napplet.<domain>.*` when `@napplet/sdk` exports that domain — **wrong default.** Prefer SDK wrappers for implementation calls; keep direct access for post-injection optional-domain fallback checks or true SDK gaps.
- Treating open NAP proposals as shipped package APIs — **wrong surface.** If the current packages do not export the domain/helper, use an existing shipped NAP that faithfully owns the intent or flag the gap.
- No `discoverServices`/`hasService`/`hasServiceVersion` — use injected domain property presence.
- Treating NAP-RELAY as the default data layer — **wrong default.** Use `outbox` for normal event reads/publishes, `common` for social actions, `lists` for list mutations, `count` for counts, and `dm` for messages. Use `relay` only when the spec names a relay-local escape hatch.
- Storage is `nappletStorage`-backed via `storage.*` — there is no `nappletState`/`nappStorage`/`nappState` import.
- Never `localStorage`/`fetch`/`<img src=externalUrl>`/`WebSocket` — the sandboxed napplet model delegates that authority to the shell. Use `storage` and `resource`.
- Never call `window.nostr` — it isn't installed. Sign/publish via `outbox.publish` or higher-level NAPs; identity is read-only.
- `publish()`/`query()` are async — `await` them; errors surface as structured results or rejections depending on the domain.
- `outbox.query()` is one-shot; `outbox.subscribe()` is the live stream.
- **JS must be inline.** A napplet is one `srcdoc` `index.html` with an opaque origin — an external `<script src>` has nothing to fetch. `artifactMode: 'single-file'` folds assets and keeps inline scripts.
- Don't trust upstream `Content-Type` for resource MIME; the shell delivers a byte-sniffed `mime`.
