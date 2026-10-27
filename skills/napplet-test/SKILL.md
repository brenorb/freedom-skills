---
name: napplet-test
description: Use to verify a napplet before publishing - build, run protocol conformance with napplet-conformance (real Chromium, reference shell), interpret failures, audit the OUTBOX-first boundaries and forbidden browser-authority surfaces, confirm the single-file artifact, run the applet UI checks (no title header, four frame sizes, both themes, minimum notice), scenario smoke tests, Paja preview, and CI wiring. Run after napplet-build, before shipping.
compatibility: CLI workflows assume `@napplet/cli` 0.13.0; package versions are independent, so verify installed SDK types.
license: MIT
metadata:
  version: "0.2.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
  upstream_sha: "6c4dafd20142cade5a51ae049beecfef7c8f7c2e"
  upstream_cli: "0.13.0"
  upstream_sdk: "0.30.0"
  upstream_source: "https://github.com/napplet/web/tree/6c4dafd20142cade5a51ae049beecfef7c8f7c2e/skills/napplet-test"
---

# Testing a Napplet

Conformance proves the build speaks NIP-5D inside a real `sandbox="allow-scripts"` iframe driven by a reference shell, catching malformed envelopes, manifest problems, boot failures, and forbidden browser-authority references locally. Truth: NIP-5D (<https://github.com/nostr-protocol/nips/pull/2303>) and the NAPs (<https://github.com/napplet/naps>). A check that fails a spec-faithful napplet but passes only this toolchain is a tooling bug — flag it; do not work around it.

## Step 1 — Build, then test the build

```bash
pnpm verify              # template guidance test + type-check + single-file build
pnpm test:conformance    # napplet-conformance ./dist → exit 0 conformant, 1 non-conformant, 2 usage/runtime error
npx napplet-conformance ./dist        # package-manager agnostic
napplet-conformance --ui ./dist       # live visual report
```

Conformance runs against `./dist` (prefers `dist/index.html`). Never test source.

## Step 2 — Interpret failures (fix the napplet, not the check)

- **Boot failure** — the runtime did not inject `window.napplet` before app code ran, or a top-level throw blocked boot.
- **Malformed envelope** — a message that is not a valid `{ type: "domain.action", … }` for its NAP; re-check the SDK call arguments.
- **Manifest problem** — missing/invalid signed manifest tags. Confirm current NIP-5D kind/d cardinality, one direct artifact `x` hash, non-empty description content, and `R`/`O` domains. Legacy path/aggregate events need explicit migration; see `napplet-migrate`.
- **Forbidden global** — the bundle references `fetch`, `localStorage`, `window.nostr`, `XMLHttpRequest`, `WebSocket`, … (static scan; unreachable references flag too). Replace with `resource` / `storage` / `outbox`, or prove and document a tooling false positive.

## Step 3 — Boundary audit

| Check | Expected |
| --- | --- |
| Normal social reads / publishes | `outbox`, `common`, `lists`, `count`, `dm` — not default `relay` |
| Any `relay.subscribe` / `relay.publish` | A comment or spec note naming the relay-local escape hatch |
| Signing / encryption | No `window.nostr`, keys, local signing, app-owned encryption |
| Relay routing | No NIP-65 resolver, relay pool, WebSocket client, fanout policy in the napplet |
| Network and media bytes | No `fetch`, XHR, WebSocket, external `<img src>`; `resource` instead |
| Persistence | No `localStorage`, IndexedDB, cookies; `storage` instead |
| Optional-domain gating | `window.napplet?.domain` after injection; never wait on optional `shell.ready()` / `shell.supports()` or service probes |
| `requires` / `optional` | Bare domain names for every used integration; required and optional lists match the design and deployment event |

```bash
grep -RInE "fetch\\s*\\(|XMLHttpRequest|WebSocket|localStorage|sessionStorage|indexedDB|document\\.cookie|window\\.nostr|<img[^>]+src=['\\\"]?https?:|<script[^>]+src=['\\\"]?https?:|<link[^>]+href=['\\\"]?https?:" src dist index.html
```

Any hit in authored or bundled napplet code is removed or explained as a tooling false positive before shipping.

## Step 4 — Artifact

`dist/index.html` is one self-contained file: inline JS, folded assets, no external `<script src>` (opaque-origin `srcdoc` has nothing to fetch). `artifactMode: 'single-file'` produces it; verify by inspecting the file, not by trusting the config.

### Check the event that will be published

Run `napplet deploy --dry-run --json --format current` and inspect the final unsigned manifest template, not only the Vite config or runtime preview. Compare its `R` and `O` domains with the design and SDK usage, including optional theme, persistence and social integrations. Do not sign or publish as part of local verification. If a signed event already exists, inspect it offline and compare its declarations with the dry-run template. This is an authoring verification step following [NIP-5D, Manifest and Required and Optional Capabilities](https://github.com/nostr-protocol/nips/pull/2303); declarations do not grant runtime permissions.

If the build declares capabilities but the deployment drops or reclassifies them, report a publishing-tool defect. Legacy serialization cannot preserve the required/optional distinction; use current-format tooling when that distinction is needed. Do not claim the integration is complete from a successful preview alone.

## Step 5 — Applet UI checks (`napplet-ui`)

Serve through Paja (Step 7) or the conformance UI, then resize the frame / use the browser device toolbar:

| Frame | Must hold |
| --- | --- |
| `200×160` | Primary action reachable, no overflow, no clipped controls, no title header |
| `320×560` | Single column, readable, inline states |
| `900×600` | Full labels, list + detail where the product has one |
| Largest available (or `2400×1200`) | Frame *used*: more rows/columns/detail — not a centered column with dead margins |

At every frame, in both a dark and a light runtime theme: no napplet name / tagline / eyebrow / masthead / footer; `html`, `body`, and root backgrounds follow the theme; loading / empty / error / signed-out states render compact and inline; if a minimum size is declared, the notice appears exactly below it, is readable, and the app resumes intact above it. Record the frames and themes checked.

## Step 6 — Scenario smoke tests

- **Signed-out:** `identity.getPublicKey()` returns `""`; publish / list / DM actions degrade with an inline state.
- **OUTBOX options:** only current fields — `getEvent`: `author`, `relays`, `timeoutMs`; `query` / `subscribe`: `authors`, `relays`, `limit`, `timeoutMs`; `publish`: `relays`, `toOutbox`, `toInboxes`. No `strategy`, subscribe `live`, publish `timeoutMs`, or `outbox.eose`.
- **Optional domain absent:** remove it from the mock runtime; the affordance hides or falls back, nothing else breaks.
- **Theme change:** emit a theme change; the whole surface repaints. A dark card on a white page is a failed integration.
- **Escape hatch:** if `relay` is used, exercise the relay-local behavior and teardown.
- **Teardown:** subscriptions and object URLs are released when the view goes away.

## Step 7 — Runtime preview

```bash
napplet paja -- pnpm vite --host 127.0.0.1
```

Report the Paja URL. If `napplet`, Kehto, or Paja is not installed, report the exact missing prerequisite and leave the manual runtime check open; never present the raw Vite URL as a napplet preview.

## Step 8 — CI

```yaml
- run: pnpm build
- run: npx napplet-conformance ./dist   # non-zero exit fails the job
```

Cache Playwright's Chromium. Green conformance + a clean boundary audit + a self-contained single-file build + the four-frame UI check = ready to publish.
