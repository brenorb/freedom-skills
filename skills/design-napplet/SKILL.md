---
name: design-napplet
description: Use FIRST when planning a napplet (sandboxed Nostr iframe app), before writing code - turns an app idea into a concrete build spec covering every current package-implemented NAP domain, required vs optional shell domains, sandbox/loading constraints, OUTBOX-first event routing, and a responsive layout that survives any viewport from full-screen to a tiny widget.
metadata:
  version: "0.1.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
---

# Designing a Napplet

Run this before `build-napplet`. Output a short spec the build step executes against. Do not write app code here. If the task is porting an existing Nostr app, run `port-nostr-app` first to identify the boundaries that must be replaced.

## What a napplet is

A napplet is a single self-contained `/index.html` loaded by a host **shell** into an iframe with `sandbox="allow-scripts"` (no `allow-same-origin`, opaque origin). It talks to the shell over `postMessage` using the NIP-5D JSON envelope. The shell owns identity, signing, relays, storage, and network. The napplet owns UI and logic only. Protocol is defined by canonical NIP-5D (<https://github.com/nostr-protocol/nips/pull/2303>) and the NAPs track (<https://github.com/napplet/naps>) — never invent surface; if you need something undefined, flag it.

## Sandbox Authority Contract

Design as if direct browser authority does not exist. A valid spec must name the
NAP boundary for every capability:

- External bytes (ROMs, WASM side files, images, avatars, media, fonts, JSON)
  are bundled into the single-file artifact or flow through `resource`.
- Persistence flows through `storage`; never browser storage, cookies, or a
  local database.
- Nostr reads and publishes flow through `outbox`, `common`, `lists`, `count`,
  `dm`, or an explicit `relay` escape hatch.
- External navigation flows through `link`; external media/playback policy
  flows through `media` when the shell owns that session boundary.

If the design would require `fetch`, `XMLHttpRequest`, `WebSocket`,
`localStorage`, `sessionStorage`, IndexedDB, cookies, external scripts/styles,
external images, direct relay pools, or app-owned signing, the design is not a
napplet yet. Redesign it around a shipped NAP or flag the missing capability.

## Constraints that drive every design decision

- **No ambient network.** `fetch`, `XMLHttpRequest`, `WebSocket`, `<img src=https://…>`, and `<link href=https://…>` are outside the napplet authority boundary. All external bytes flow through `resource.bytes(url)`. Design around request/await, not direct loads.
- **No direct persistence.** `localStorage`/`IndexedDB`/cookies throw or are inert. State goes through `storage` (512 KB quota, async).
- **No keys.** The napplet never signs. It hands templates to the shell. Never plan a flow that needs a raw privkey.
- **Single file.** Ships as one `index.html` (JS inline, assets folded in). No runtime code-splitting, no external `<script src>`. Keep the bundle lean.
- **Read-only identity.** You can read the user's pubkey/profile/follows; you cannot decrypt or impersonate.

## Step 1 — Pick capabilities (NAPs)

Map each feature to the NAP domain that provides it. Use only domains exported
by the current `@napplet/nap` / `@napplet/sdk` packages. Current packages do not
expose `window.napplet.shell`, `shell.ready()`, or `shell.supports(...)`; do not
design a private readiness handshake or generic service probe. A conforming
runtime installs `window.napplet` before app module code runs. If a host exposes
domains later than that, flag a runtime/package gap.

Use `@napplet/sdk` wrappers for calls. Name the helper or namespace the build
should import for each domain. Use direct `window.napplet?.domain` checks only
as optional-domain fallback checks after runtime injection; do not make direct
`window.napplet.<domain>.*` calls the implementation surface when SDK helpers
exist. If a NAP is not in this package inventory, do not design against it as
usable API — flag a package/spec gap.

| Need | Implemented package NAP domain |
| --- | --- |
| Read/publish Nostr events where relay choice affects correctness | `outbox` |
| Low-level relay access to one explicit relay, relay diagnostics, or protocols outside the outbox model | `relay` |
| Common public social actions: profile lookup, follows, follow/unfollow, reactions, reports, NIP-19 helpers | `common` |
| Safe NIP-51 / NIP-65 list mutations | `lists` |
| Counts for reactions, replies, reposts, quotes, reports, followers | `count` |
| Direct-message UI and message send/history/live delivery | `dm` |
| User pubkey / public identity snapshots | `identity` (read-only) |
| Persist app state | `storage` |
| Talk to other napplets | `inc` |
| Fetch avatars / external bytes | `resource` |
| Upload user-selected files or blobs through shell policy | `upload` |
| Open external links through shell prompting/policy | `link` |
| Invoke or expose app-to-app actions | `intent` |
| User-configurable settings | `config` |
| Match shell light/dark/accent | `theme` |
| Keyboard shortcuts, forwarded key events, action keybindings | `keys` |
| Playback / now-playing / media command sessions | `media` |
| Notifications, badge counts, notification actions | `notify` |
| ContextVM / MCP-style native tool bridge | `cvm` |
| Bluetooth LE / GATT access through shell policy | `ble` |
| Serial-port access through shell policy | `serial` |
| Virtual filesystem access through shell policy, including byte reads/writes | `fs` |
| WebRTC signaling/session mediation | `webrtc` |

The deprecated `ifc` package subpath is an INC compatibility alias; choose
`inc` for new work. Every NAP is **voluntary**: assume a domain may be absent and
degrade gracefully unless it is a hard manifest requirement.

### Cross-napplet roles and messages

For an `intent` feature, record the role slug and stable, queryless convention
identity that callers use: `napplet:<archetype>/<intent>`. A published archetype
advertises one contract in an `['archetype', slug, convention]` manifest tag, for example `['archetype', 'note', 'napplet:note/open']`.

For `inc`, name the exact opaque topic the feature emits or subscribes to. Each
subscription receives one `IncEvent` containing a runtime-attested sender and
optional payload. Use topics such
as `napplet:note/open`, `napplet:profile/open`, or `napplet:dm/open`. NAP-INC
`emit(topic, payload?)` may use `napplet:profile/open?pubkey=abc123` as
developer-facing shorthand: the runtime transposes its shallow text query into
payload and routes the stable queryless topic `napplet:profile/open`. Specify
subscriptions against that stable queryless topic. The build must treat incoming
payloads as untrusted and validate them against a real upstream convention when
one exists.

This query rule applies only to outbound NAP-INC `emit(topic, payload?)`.
Literal `+` remains a plus after percent decoding; fragments, malformed percent
encoding, repeated decoded names, and query plus explicit payload reject
synchronously. Plan a queryless topic with explicit payload for structured or
non-text data.

For NAP-INTENT, plan `invoke(request)` or
`open(archetype, payload?, opts?)`. Archetype routing and optional
convention-based payload interpretation are orthogonal. Results expose required
`ok`, `archetype`, `action`, and `handled` fields.

Subscriptions, manifest discovery, and routing retain exact matching without
query parsing, prefix, wildcard, canonicalization, payload-schema, or
multi-convention behavior. Defer to the living [NAP-INC](https://github.com/napplet/naps/blob/master/naps/NAP-INC.md)
and [NAP-INTENT](https://github.com/napplet/naps/blob/master/naps/NAP-INTENT.md) documents for the
living normative contract.

### NAP-THEME is a whole-surface concern

If the napplet has a visual UI, plan theme integration even when it is optional.
Do not stop after coloring buttons or accents. The build spec must include a
theme application function that maps `theme.colors.background` and
`theme.colors.text` onto `:root`, `html`, `body`, and the app root as appropriate,
then maps primary, surface, border, and muted tokens to the component system.
Subscribe to `themeOnChanged` and repaint all of those tokens. The fallback
palette must set an explicit page background, so a dark design never falls back
to a white body with dark cards. Preserve readable contrast in dark and light
themes.

## Step 1.5 — Choose The Right Nostr Boundary

Default to the highest-level NAP that owns the user intent:

| Feature shape | Prefer | Do not start with |
| --- | --- | --- |
| Timeline/feed/profile/event reads that should follow author relay lists | `outbox.query` / `outbox.subscribe` | Manual `relay.subscribe` plus app-owned relay discovery |
| Publishing user-authored public events | `outbox.publish` | `relay.publish` unless the outbox model is wrong for the feature |
| Follow/unfollow/react/report/profile lookup/NIP-19 helpers | `common` | Hand-built events plus relay publish |
| Mute/pin/bookmark/follow-set/relay-list mutation | `lists` | Editing replacement list events locally |
| Counts or badges where event bodies are not needed | `count.query` | Downloading matching events through relay/outbox |
| Direct-message products | `dm` | Implementing NIP-04/NIP-17/NDR crypto and relay routing inside the napplet |
| One explicit relay, group relay, raw relay diagnostics, or a protocol not expressible through outbox/common/lists/count/dm | `relay` | Treating relay as the default app data layer |

Use `relay` as an escape hatch only when the feature genuinely needs relay-local semantics. If the app is social, publishing user events, reading authors' events, or mutating user-owned Nostr state, it is almost always `outbox`, `common`, `lists`, `count`, or `dm`.

## Step 2 — Declare requirements vs. optional

- **Hard requirement** → list bare NAP domain names in the vite-plugin
  `requires: [...]` only when the napplet cannot perform its core task without
  that domain, so a shell can refuse/inform up front.
- **Optional enhancement** → no manifest entry; guard after runtime injection
  with `if (window.napplet?.domain)` and provide a fallback.

State which is which in the spec. Prefer optional + graceful degradation over
hard requirements. Do not add `keys` to `requires` when local buttons, menus,
text input, click/tap controls, or other non-reserved shortcuts let the napplet
function without shell-managed key reservation.

## Step 3 — Responsiveness is mandatory

A shell may render a napplet at **any** size — full-screen tab, half-pane, sidebar, or a tiny embedded widget — and resize it live. Design fluid, not fixed:

- Use container-relative units, flexbox/grid, `clamp()`, and (where helpful) container queries. Never assume a viewport width.
- Define behavior at the extremes: a usable **tiny** state (compact/iconified, hide non-essential chrome) and a comfortable **large** state.
- Test the smallest size you'll allow and the largest; ensure no horizontal overflow and no clipped controls at either end.
- Honor `theme` so the napplet visually belongs in its host.

## Step 4 — Write the spec

Produce a short block the build step consumes:

```
nappletType: <kebab d-tag, e.g. "note-feed">
purpose: <one line>
NAPs used: outbox (req), common (opt), identity (opt), storage (req), resource (opt)
requires: []        # hard requirements only; keep optional enhancements out
optional domains and fallbacks: resource -> show initials when avatar fetch unavailable; keys -> use buttons/menu when shell key reservation is absent
SDK helpers: outbox.query, outbox.subscribe, common.getProfile, storage.getItem, resource.bytes
config schema: <fields or "none">
archetype metadata: <none, or slug + stable queryless convention identity>
INC topics and payload validation: <none, or exact opaque topic + upstream convention/local validation boundary>
intent dispatch: <none, or invoke/open request + handling-result behavior>
layout: <tiny state> / <large state>, responsive strategy
theme: NAP-THEME optional/required; root background, text, surface, border, primary, muted mappings; fallback palette; change subscription
data flow: <outbox queries/subscriptions/publishes, social actions, stored keys>
relay escape hatches: <none, or exact reason + why outbox/common/lists/count/dm do not apply>
```

Hand this to `build-napplet`. Then verify with `test-napplet`.
