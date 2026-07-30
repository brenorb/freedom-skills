---
name: test-napplet
description: Use to verify a napplet before publishing - run protocol conformance with the @napplet/conformance-cli runner (real Chromium, reference shell), interpret failures, confirm OUTBOX-first boundaries, the single-file artifact, runtime guard, and CI wiring. Run after build-napplet, before shipping.
metadata:
  version: "0.1.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
---

# Testing a Napplet

Conformance proves the build speaks NIP-5D correctly inside a real `sandbox="allow-scripts"` iframe driven by a reference shell — catching malformed envelopes, manifest problems, boot failures, and forbidden browser-authority references locally instead of after publishing. Truth: NIP-5D (<https://github.com/nostr-protocol/nips/pull/2303>) + NAPs (<https://github.com/napplet/naps>).

## Sandbox Authority Contract

Testing is not green if the napplet still owns browser authority that belongs to
the shell. Treat any of these in served source or built output as a release
blocker:

- `fetch`, `XMLHttpRequest`, `WebSocket`, relay pools, direct NIP-65 routing, or
  app-owned network fanout.
- `localStorage`, `sessionStorage`, IndexedDB, cookies, or other browser-local
  persistence.
- External network-loaded `<script>`, stylesheet, image, audio, video, font, CSS
  URL, or dynamic import.
- `window.nostr`, raw keys, app-owned signing, or app-owned encryption.

Expected replacements are `resource` for bytes, `storage` for state, `outbox` /
`common` / `lists` / `count` / `dm` for social Nostr behavior, `relay` only for
a documented relay-local escape hatch, and `link` for external URL opening.

## Step 1 — Build first

```bash
pnpm build
```

Conformance runs against built output (`./dist`, preferring `dist/index.html`, falling back to `./index.html`). Always test the build, not source.

## Step 2 — Run conformance

`napplet-conformance` (from `@napplet/conformance-cli`) loads the build into headless Chromium, drives the protocol with a reference shell, runs the check catalog, and sets the exit code.

```jsonc
// package.json
{ "scripts": { "test:conformance": "napplet-conformance ./dist" } }
```

```bash
pnpm test:conformance          # exits non-zero on any error-severity failure
# package-manager agnostic:
npx napplet-conformance ./dist
```

Exit codes: `0` conformant, `1` non-conformant, `2` usage/runtime error.

For a visual, live report (like `vitest --ui`):

```bash
napplet-conformance --ui ./dist
```

## Step 3 — Interpret failures

Failures map to a NIP-5D / NAP requirement — fix the napplet, not the check. Common classes:

- **Boot failure** — the runtime did not inject `window.napplet` before app code ran, or a top-level throw blocked boot.
- **Malformed envelope** — a message that isn't a valid `{ type: "domain.action", … }` for its NAP. Re-check arguments to the `window.napplet.*` call.
- **Manifest problem** — missing or invalid signed manifest tags. Confirm the
  build/deploy tool emitted the NIP-5A `d`, `path`, and aggregate `x` tags;
  required capabilities belong in `requires` tags on that manifest event.
- **Forbidden global** — the bundle references `fetch`, `localStorage`, `window.nostr`, `XMLHttpRequest`, `WebSocket`, etc. Replace with `resource.bytes` / `storage` / `relay`. (Static scan — even unreachable references flag.)

A check that fails a spec-faithful napplet but passes only this toolchain is a tooling bug — flag it; do not work around it.

## Step 4 — Boundary Audit

Before publishing, inspect source and built output for wrong-layer code:

| Check | Expected |
| --- | --- |
| Normal social reads/publishes | `outbox`, `common`, `lists`, `count`, or `dm`, not default `relay` |
| Any `relay.subscribe` / `relay.publish` use | A comment or spec note naming the relay-local escape hatch |
| Signing/encryption | No `window.nostr`, private keys, local signing, or app-owned encryption |
| Relay routing | No app-owned NIP-65 resolver, relay pool, WebSocket relay client, or relay fanout policy |
| Network and media bytes | No direct `fetch`, `XMLHttpRequest`, `WebSocket`, or external `<img src>`; use `resource` |
| Persistence | No `localStorage`, `IndexedDB`, cookies, or direct filesystem state; use `storage` |
| Optional-domain fallback checks | `window.napplet?.domain` after runtime injection; no `window.napplet.shell`, `shell.ready()`, `shell.supports(...)`, or generic service probing |

If a direct relay use remains, prove why `outbox`, `common`, `lists`, `count`, and `dm` do not fit. Otherwise refactor before shipping.

Also scan for direct browser authority with exact strings before completion:

```bash
grep -RInE "fetch\\s*\\(|XMLHttpRequest|WebSocket|localStorage|sessionStorage|indexedDB|document\\.cookie|window\\.nostr|<img[^>]+src=['\\\"]?https?:|<script[^>]+src=['\\\"]?https?:|<link[^>]+href=['\\\"]?https?:" src dist index.html
```

Any hit in authored or bundled napplet code must be removed or explained as a
tooling false positive before shipping.

## Step 5 — Confirm the artifact & guard

- **Single file:** the published napplet is one `index.html` with inline JS (opaque-origin `srcdoc`, no external `<script src>`). Use `artifactMode: 'single-file'`. Verify `dist/index.html` is self-contained.
- **Runtime guard:** opened without a runtime it shows an explanatory modal rather than failing silently. For standalone manual testing, opt out before the shim loads via `window.__NAPPLET_ALLOW_STANDALONE__ = true`.

## Step 6 — Scenario Smoke Tests

Exercise the feature against the NAP domains it declares:

- Signed-out path: identity returns `""`; app degrades without publish/list/dm actions.
- OUTBOX path: current option fields only: `outbox.getEvent` uses `author`, `relays`, `timeoutMs`; `outbox.query` / `outbox.subscribe` use `authors`, `relays`, `limit`, `timeoutMs`; `outbox.publish` uses `relays`, `toOutbox`, `toInboxes`. No `strategy`, subscribe `live`, publish `timeoutMs`, or `outbox.eose`.
- Optional-domain path: remove an optional domain from the mock runtime and verify fallback UI.
- Theme path: run with dark and light themes, verify `html`/`body`/app-root
  backgrounds as well as text, surfaces, borders, and primary colors, then
  emit a theme change and verify the whole surface repaints. A dark card on a
  white page is a failed theme integration.
- Escape hatch path: if `relay` is used, test the explicit relay-local behavior and teardown.

## Step 7 — Runtime Preview

Conformance is not a user preview. When a local shell is available, launch the
project through Paja and report its URL:

```bash
napplet paja -- pnpm vite --host 127.0.0.1
```

The final preview link must be the Paja/runtime URL, not the underlying Vite
server URL. If `napplet`, Kehto, or Paja is not installed, report the exact
missing prerequisite and leave the manual runtime check open; never present
the raw Vite URL as a valid napplet preview.

## Step 8 — CI

Run conformance headless in CI: cache Playwright's Chromium, build, then run the CLI. See `.github/workflows/conformance.yml` in the napplet monorepo for the reference pattern.

```yaml
- run: pnpm build
- run: npx napplet-conformance ./dist   # non-zero exit fails the job
```

Green conformance + a self-contained single-file build = ready to publish.
