---
name: napplet-design
description: Use FIRST when planning a napplet (sandboxed Nostr iframe applet), before any code - turns an idea into a short build spec - the sandbox authority contract, which shipped NAP domains own each feature (OUTBOX-first, relay as escape hatch), hard requires vs optional fallbacks, the form-factor plan (compact applet, any size from widget to full screen, declared minimum only if the UI truly breaks), theme, and data flow. Output is consumed by napplet-build.
compatibility: CLI workflows assume `@napplet/cli` 0.13.0; package versions are independent, so verify installed SDK types.
license: MIT
metadata:
  version: "0.2.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
  upstream_sha: "6c4dafd20142cade5a51ae049beecfef7c8f7c2e"
  upstream_cli: "0.13.0"
  upstream_sdk: "0.30.0"
  upstream_source: "https://github.com/napplet/web/tree/6c4dafd20142cade5a51ae049beecfef7c8f7c2e/skills/napplet-design"
---

# Designing a Napplet

Run this before `napplet-build`. Output the spec block at the end; do not write app code here. If the starting point is an existing Nostr app, run `napplet-port` first. Protocol truth is canonical NIP-5D (<https://github.com/nostr-protocol/nips/pull/2303>) and the NAPs track (<https://github.com/napplet/naps>) — never invent surface; flag gaps.

## What a napplet is

A single self-contained `/index.html` that a host **runtime** (shell) loads into an iframe with `sandbox="allow-scripts"` (no `allow-same-origin`, opaque origin) and talks to over `postMessage` using the NIP-5D JSON envelope. The shell owns identity, signing, relays, storage, network, and the window chrome (it shows the napplet's name). The napplet owns UI and logic only. It is an **applet**: small, focused software that may be placed at any size — see `napplet-ui`.

## Sandbox authority contract

Design as if direct browser authority does not exist. A valid spec names the NAP boundary for every capability:

- External bytes (images, avatars, media, fonts, JSON, WASM side files) are bundled into the single-file artifact or flow through `resource`.
- Persistence flows through `storage` (async, 512 KB, scoped) — never browser storage, cookies, or a local database.
- Nostr reads and publishes flow through `outbox`, `common`, `lists`, `count`, `dm`, or a named `relay` escape hatch. The napplet never holds keys or signs.
- External navigation flows through `link`; playback sessions through `media` when the shell owns that boundary.
- Single file: JS inline, assets folded in, no runtime code-splitting, no external `<script src>`.

If the design needs `fetch`, `XMLHttpRequest`, `WebSocket`, `localStorage`, IndexedDB, cookies, external scripts/styles/images, relay pools, `window.nostr`, or app-owned signing, it is not a napplet yet — redesign around a shipped NAP or flag the missing capability.

## Step 1 — Scope one job

Write the single-purpose job in one line. If the request is a whole app, split it into focused napplets (feed, composer, profile, DMs, settings…) unless the user explicitly wants one compound napplet that still works in a small frame. Cross-napplet handoff uses `inc` / `intent` (`napplet-interop`).

## Step 2 — Map features to shipped NAP domains

Use only domains the current `@napplet/sdk` exports (`napplet-sdk` lists them). Default to the highest-level NAP that owns the user intent:

| Feature shape | Prefer | Do not start with |
| --- | --- | --- |
| Feed / profile / event reads that should follow author relay lists | `outbox.query` / `outbox.subscribe` | Manual `relay.subscribe` + app relay discovery |
| Publishing user-authored events | `outbox.publish` | `relay.publish` |
| Follow / unfollow / react / report / profile lookup / NIP-19 | `common` | Hand-built events + publish |
| Mute / pin / bookmark / follow-set / relay-list mutation | `lists` | Editing replaceable lists locally |
| Counts or badges without event bodies | `count.query` | Downloading events to count them |
| Direct messages | `dm` | Implementing NIP-04/17 crypto and routing |
| Current user pubkey / snapshots | `identity` (read-only) | Polling or `window.nostr` |
| App state | `storage` | `localStorage` |
| Avatars, images, JSON, media bytes | `resource` | `fetch`, `<img src=https://…>` |
| Uploads, external links | `upload`, `link` | Direct network / `window.open` |
| Host look | `theme` | App-owned theme detection |
| Keyboard interaction | Ordinary buttons and browser controls | Assuming unmerged shell action-registration APIs |
| Notifications, playback, device bridges | `notify`, `media`, `cvm`, `ble`, `serial`, `fs`, `webrtc` | Browser APIs |
| One explicit relay, diagnostics, protocols outside the outbox model | `relay` | Treating relay as the data layer |


Every NAP is voluntary: assume a domain may be absent and name the fallback. `relay` needs an exact written reason; if none exists it is wrong. Do not gate a domain on `shell.ready()` / `shell.supports()` or any capability probe — a conforming runtime installs `window.napplet` before module code runs, and the optional `shell` domain only describes the environment.

## Step 3 — Hard requirements vs optional enhancements

This non-normative authoring guidance follows [NIP-5D, Required and Optional Capabilities](https://github.com/nostr-protocol/nips/pull/2303). Record both lists explicitly, even when empty; runtime presence checks do not write manifest declarations.

- **Hard** (napplet cannot do its one job without it) → bare domain names in the vite-plugin `requires: [...]` so a shell can refuse the load up front.
- **Optional** → declare in `optional: [...]`; gate after injection with `if (window.napplet?.domain)` and give a fallback.

Put each used optional integration in the vite-plugin `optional: [...]` list as well as guarding its runtime calls. Current tooling emits `R` for `requires` and `O` for `optional`. Keep these declarations aligned when features are added or removed; list only domains actually used.

Prefer optional + graceful degradation. `theme`, `notify`, `resource`, `inc`, `intent` are almost never hard.

## Step 4 — Form factor plan (mandatory)

Decide these now; `napplet-ui` has the rules and defaults:

- **No title header.** The runtime shows the name; the spec does not include an app title, tagline, or masthead.
- **Density:** `compact` unless the product is a reader/viewer that justifies larger type — state the deviation.
- **Tier behavior:** what the napplet shows at `tiny (<240px)`, `compact (240–480)`, `regular (480–900)`, `wide (>900)`, and at short heights. The wide tier must *use* the space (more columns/rows/detail), not center a column.
- **Minimum size:** `none` (degrade instead) or exact `minWidth × minHeight` plus why, with the notice text shown below it.
- **Theme:** whole-surface mapping (background/text/primary → html/body/root + tokens), fallback palette, dark and light both checked.
- **States:** inline compact loading / empty / error / signed-out.

## Step 5 — Write the spec

```
nappletType: <kebab d-tag, e.g. "note-feed">
purpose: <one line, one job>
NAPs used: outbox (req), storage (req), identity (opt), common (opt), resource (opt)
requires: [outbox, storage]        # hard only
optional: [identity, common, resource]
optional domains and fallbacks: identity -> anonymous view; resource -> initials avatar; common -> hide react/follow
SDK helpers: outbox.query, outbox.subscribe, outbox.publish, storage.getItem/setItem, identity.getPublicKey/onChanged
data flow: <queries / subscriptions / publishes / stored keys>
relay escape hatches: none | <exact reason outbox/common/lists/count/dm cannot cover>
interop: none | <see napplet-interop lines>
density: compact | <deviation + reason>
tiers: tiny=<…> compact=<…> regular=<…> wide=<…> short-height=<…>
minimum size: none | <W×H + reason + notice text>
theme: optional | required; fallback palette <bg/fg/primary>
states: loading=<…> empty=<…> error=<…> signed-out=<…>
```

Hand this to `napplet-build`; verify with `napplet-test`. When the request includes icon artwork, use `napplet-icon` to design and generate it from the app's purpose and visual direction. Carry the selected asset and integration notes into the build handoff.
