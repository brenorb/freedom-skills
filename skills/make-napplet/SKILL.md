---
name: make-napplet
description: Use when a user asks to create, build, implement, prototype, or port a complete napplet in one prompt. Orchestrates the napplet skills end to end, covers every current package-implemented NAP domain, keeps normal social reads and publishes OUTBOX-first, routes shortcuts/keybindings to NAP-KEYS, and treats NAP-RELAY as an explicit escape hatch only.
metadata:
  version: "0.3.0"
  package: "@napplet/skills"
  repository: "https://github.com/napplet/web"
  source: "https://github.com/napplet/web/tree/03ad65b66413e5798536ef48695ffc4c2508f2c3/packages/skills/skills/make-napplet"
---

# Making A Napplet End To End

Use this as the top-level workflow for "build me a napplet" prompts. Do not skip
straight to code. The goal is a working, conformant napplet with the right shell
boundaries on the first implementation pass.

Protocol truth: NIP-5D (<https://github.com/nostr-protocol/nips/pull/2303>) and
the NAPs track (<https://github.com/napplet/naps>). Use the current
`@napplet/*` package surface in this repo or the installed package version.
Never invent message types, domains, manifest tags, loading rules, or shell
authority to satisfy a prompt.

## Sandbox Authority Contract

Before any design or code, treat the iframe sandbox as a hard boundary:

- Napplet code has no ambient browser authority. Do not use `fetch`,
  `XMLHttpRequest`, `WebSocket`, `localStorage`, `sessionStorage`, IndexedDB,
  cookies, external `<script src>`, external `<link href>`, or external
  `<img src>` in generated napplet code.
- External bytes, including ROMs, WASM side files, avatars, images, audio,
  video, fonts, and JSON, must be either bundled into the single-file artifact
  or requested through `resource.bytes` / `resource.bytesMany`.
- Persistent state goes through `storage`; relay/network behavior goes through
  `outbox`, `common`, `lists`, `count`, `dm`, or an explicit `relay` escape
  hatch; external links go through `link`.
- If a library tries to own browser storage or network internally, either
  configure it onto shell-provided NAPs, stub the forbidden path so it never
  runs, bundle the required bytes at build time, or flag the library as
  unsuitable for a strict napplet. Do not ship a napplet that "mostly works"
  until it hits a browser `NetworkError`.

## Decision Tree

| User request | First step |
| --- | --- |
| New napplet from an idea | Run `design-napplet`, then `build-napplet`, then `test-napplet` |
| Port an existing Nostr app/client/widget | Run `port-nostr-app`, then `design-napplet`, then `build-napplet`, then `test-napplet` |
| Add a feature to an existing napplet | Re-run the relevant part of `design-napplet` for the feature boundary, then build and test |
| Debug or verify a built napplet | Run `test-napplet`; only edit after reproducing the failure |
| Request needs a NAP/domain not shipped by current packages | Stop and flag the gap; do not fake it with local APIs |

## Step 1 - Establish Scope

Write a small build brief before editing:

```
deployment name / d-tag:
CLI metadata initialized:
new build or port:
boilerplate substrate:
single-purpose job:
must-have user flows:
optional user flows:
target shell assumptions:
known protocol/package gaps:
```

If the request is a full app, split it into focused napplets unless the user
explicitly requires one compound napplet and that shape is still usable in a
small iframe.

## Step 1.5 - Triage The Project And Toolchain

Before choosing commands, inspect the directory and available tools. Do not
assume the CLI, Kehto/Paja, or the boilerplate exists.

```bash
pwd
command -v napplet || true
command -v kehto || command -v paja || true
test -f package.json && cat package.json
test -f .napplet/config.json && cat .napplet/config.json
test -f vite.config.ts && sed -n '1,220p' vite.config.ts
find . -maxdepth 2 -type f | sort | sed -n '1,160p'
```

Choose one starting state:

| State | Action |
| --- | --- |
| `napplet` unavailable | Stop and tell the user to install the standalone CLI, or use the repository's documented local CLI path. Do not pretend `create`, `init`, or `paja` ran. |
| Empty directory | Run `napplet create <directory>`, enter it, then run `napplet init`. |
| Boilerplate directory with no product work | Preserve the substrate, run `napplet init` if metadata is absent, then implement the product. |
| Existing napplet with `.napplet/config.json` and generated scripts | Treat it as initialized; inspect metadata and scripts, then edit product surfaces. |
| Brownfield app based on the boilerplate | Preserve compatible generated scripts/config and port only app-specific code; do not scaffold over it. |
| Brownfield app with no boilerplate | Run `port-nostr-app` first, then add only the equivalent current build, single-file, metadata, and conformance wiring required. Document the retrofit. |

If Kehto/Paja is unavailable, continue automated build/conformance work but
report the missing runtime as an unverified manual-preview gap. Never finish
with a raw Vite URL presented as a working napplet preview.

## Step 2 - Pick The Boundary Before Code

Default social/event boundary:

- Feeds, timelines, profiles, event lookups, search-ish reads, and normal
  publishes use `outbox`.
- Follow/unfollow/react/report/profile lookup/NIP-19 use `common`.
- NIP-51/NIP-65 list mutation uses `lists`.
- Counts use `count`.
- Direct messages use `dm`.
- User pubkey/current-user snapshots use `identity`.
- Local app state uses `storage`.
- External bytes use `resource`; uploads use `upload`.
- Cross-napplet handoff uses `inc` or `intent`. Record one stable, queryless
  convention identity such as `napplet:note/open`, `napplet:profile/open`, or
  `napplet:dm/open`; archetype metadata emits one stable, queryless convention
  identity in `['archetype', slug, convention]`.
- Keyboard shortcuts/action keybindings use `keys`.
- Playback/now-playing uses `media`; notifications/badges use `notify`.
- Settings/theme use `config` and `theme`.
- Native bridge/device/session features use `cvm`, `ble`, `serial`, or `webrtc`
  only when the user story needs that exact shell-mediated boundary.
- File browsing, directory listing, byte reads/writes, and change watching use
  `fs` — shell-mediated virtual filesystem access.
- External URL opening uses `link`.
- `relay` is only for an explicit relay-local escape hatch such as group relay
  protocols, diagnostics, or raw relay tooling outside the outbox model.

Record every relay escape hatch in the build brief. If no exact reason exists,
using `relay` is wrong.

For cross-napplet features, payloads are local choices and inbound values are
untrusted. Validate each received payload against a real upstream convention
when one exists; do not recreate numbered payload contracts or infer a payload
schema from an opaque convention name. `inc.on` receives one `IncEvent` with a
runtime-attested sender and optional payload. NAP-INC `emit(topic, payload?)` may send
`napplet:profile/open?pubkey=abc123`; the runtime transposes that shallow text
query into payload and routes the stable queryless topic
`napplet:profile/open`, which subscribers use exactly.

This is outbound emit preprocessing, not a routing rule. Literal `+` stays
plus after percent decoding. Fragments, malformed percent encoding, repeated
decoded names, and a query with explicit payload throw synchronously; use a
queryless topic with explicit payload for structured or non-text data.

NAP-INTENT dispatches through `invoke(request)` or
`open(archetype, payload?, opts?)`. Archetype routing and optional
convention-based payload interpretation are orthogonal. Results contain required
`ok`, `archetype`, `action`, and `handled` fields.

Never put query text in manifest metadata. Subscriptions, manifest discovery,
and routing keep exact matching without query parsing, prefix, wildcard,
canonicalization, or multi-convention behavior. See [NAP-INC draft PR #89](https://github.com/napplet/naps/pull/89)
and the living [NAP-INTENT document](https://github.com/napplet/naps/blob/master/naps/NAP-INTENT.md) for the
living normative contract.

## Step 3 - Run The Specialized Skills

1. For ports, run `port-nostr-app` and produce its inventory/handoff.
2. Run `design-napplet` and produce the build spec.
3. For new projects, run `napplet create <directory>`, enter it, and run
   `napplet init` before implementation. Preserve the generated package manager
   config, Vite config, scripts, layout, README/docs structure, conformance
   wiring, and CLI-owned deployment metadata.
4. Run `build-napplet` against that spec, editing only project-specific files
   such as `src/main.ts`, `src/styles.css`, `vite.config.ts` fields,
   `index.html` title/root markup, config schema, and README/docs.
5. Run `test-napplet` before reporting completion.

For a human preview, run the app through Paja:

```bash
napplet paja -- pnpm vite --host 127.0.0.1
```

Use the Paja URL printed by the runtime in the final report. A raw Vite URL is
only an asset server and is not a valid runtime preview.

Do not claim "done" after design or code alone. Done means the built artifact
passes the boilerplate validation (`pnpm verify`, `pnpm test:conformance`), any
feature-specific checks, and the boundary audit has no forbidden surfaces.

## Step 4 - Package Surface Rule

Use only domains and helpers that are shipped by the current packages. Current
package domains are:

`relay`, `identity`, `storage`, `inc`, `theme`, `keys`, `media`, `notify`,
`config`, `resource`, `cvm`, `outbox`, `upload`, `intent`, `ble`, `webrtc`,
`link`, `count`, `lists`, `serial`, `fs`, `common`, `dm`.

The deprecated `ifc` subpath is only an INC compatibility alias; new work uses
`inc`. If a NAP is not in the package-domain list above, do not implement
against it as usable API. Use an existing shipped boundary only when it
faithfully models the task, otherwise flag the missing package/spec surface.

Implementation code is SDK-first: import callable helpers from `@napplet/sdk`
when they exist. Use direct `window.napplet?.domain` access for post-injection
optional-domain fallback checks, not as the default way to call NAP methods. If
a current package domain lacks a central SDK namespace/object, use the helper
exports that `@napplet/sdk` re-exports (for example `themeGet` /
`themeOnChanged`) or flag the package gap instead of inventing a local client.

Current packages do not expose `window.napplet.shell`, `shell.ready()`, or
`shell.supports(...)`. Use `@napplet/sdk` wrappers for calls and use
`window.napplet?.domain` only as an optional-domain fallback check after runtime
injection. Do not add a private readiness handshake or generic service probing
layer to generated napplet code.

## Step 5 - Completion Checklist

- No `window.nostr`, private keys, app-owned signing/encryption, relay pools,
  direct NIP-65 routing, `localStorage`, direct `fetch`, external scripts, or
  WebSockets in napplet code.
- No `shell.ready()`, `shell.supports(...)`, `discoverServices`, or generic
  service probing. Current packages expose no `window.napplet.shell` namespace.
  Optional-domain fallback checks are `window.napplet?.domain` after runtime
  injection.
- Napplet implementation calls use `@napplet/sdk` helpers wherever available;
  direct `window.napplet.<domain>.*` calls appear only for true SDK gaps.
- Outbox calls use current option fields only:
  `outbox.getEvent`: `author`, `relays`, `timeoutMs`;
  `outbox.query` / `outbox.subscribe`: `authors`, `relays`, `limit`, `timeoutMs`;
  `outbox.publish`: `relays`, `toOutbox`, `toInboxes`.
  No `strategy`, subscribe `live`, publish `timeoutMs`, or `outbox.eose`.
- Every optional NAP is gated with a graceful fallback.
- Implement NAP-THEME across the whole surface: map background and text onto
  `html`, `body`, and the app root, then map primary, surface, border, and muted
  tokens intentionally. Subscribe with `themeOnChanged` so runtime changes
  repaint the whole UI. If theme is absent, use an explicit local fallback
  palette, including a page background; test both dark and light backgrounds.
- Every hard requirement is declared with a bare domain name in the manifest
  `requires` list, not `NAP-*`.
- Do not add `keys` to `requires` when local buttons, menus, text input, or
  click/tap controls let the napplet function without shell-managed key
  reservation.
- Shortcut/keybind features use `keys.register()` / `keys.onAction()` rather
  than app-owned global shortcut plumbing.
- The final answer includes the commands/checks that passed and any live-shell
  interoperability gap that was not tested.
- The final answer links to the Paja runtime preview, or explicitly says Paja
  was unavailable and no runtime preview was claimed. Never substitute a raw
  Vite URL.

Stop only when the napplet is implemented, verified, and does not own authority
that belongs to the shell.
