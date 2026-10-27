---
name: napplet-build
description: Use when implementing a napplet from a napplet-design spec - scaffold with `napplet create` + `napplet init`, keep the boilerplate substrate, edit only project surfaces (vite.config requires, index.html, src/main.ts, src/styles.css), strip the starter masthead and website layout per napplet-ui, call shell capabilities SDK-first (napplet-sdk), produce the single-file artifact, validate with pnpm verify + conformance, and preview through Paja. Pairs with napplet-ui, napplet-sdk, napplet-interop, napplet-test.
compatibility: CLI workflows assume `@napplet/cli` 0.13.0; package versions are independent, so verify installed SDK types.
license: MIT
metadata:
  version: "0.2.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
  upstream_sha: "6c4dafd20142cade5a51ae049beecfef7c8f7c2e"
  upstream_cli: "0.13.0"
  upstream_sdk: "0.30.0"
  upstream_source: "https://github.com/napplet/web/tree/6c4dafd20142cade5a51ae049beecfef7c8f7c2e/skills/napplet-build"
---

# Building a Napplet

Implements a `napplet-design` spec. A napplet is one self-contained `/index.html` loaded into a `sandbox="allow-scripts"` iframe; all host access is proxied over postMessage per NIP-5D (<https://github.com/nostr-protocol/nips/pull/2303>) and the NAPs (<https://github.com/napplet/naps>). Never invent wire surface; flag gaps. Before writing any markup or CSS, load `napplet-ui`; while calling shell capabilities, use `napplet-sdk`; for cross-napplet features, `napplet-interop`.

## Pre-code gate: sandbox authority

Rewrite the plan before coding if it needs any of these in napplet code: `fetch`, `XMLHttpRequest`, `WebSocket`, `localStorage`, `sessionStorage`, IndexedDB, `document.cookie`, `window.nostr`, relay pools, signing, external `<script src>` / `<link href>` / `<img src>` / `<audio|video src>` / CSS `url(https://…)` / dynamic `import("https://…")`, or any side file the `srcdoc` iframe would have to fetch. Bytes are bundled at build time or requested through `resource`; state goes through `storage`; Nostr goes through `outbox` / `common` / `lists` / `count` / `dm` (or a documented `relay` escape hatch); URLs open through `link`. If a dependency needs direct network or storage authority at runtime, stop and flag it instead of shipping.

## Step 1 — Start from the CLI scaffold

```bash
napplet create my-napplet
cd my-napplet
napplet init            # d-tag, title, description, archetype metadata → .napplet/config.yaml
pnpm install
```

`create` clones the maintained `github.com/napplet/boilerplate` template (package manager pin, Vite config, single-file build, scripts, conformance wiring, docs layout). `init` owns deployment metadata. Do not recreate `package.json`, `pnpm-lock.yaml`, `vite.config.ts`, `tsconfig`, or the scripts by hand; edit the generated project. If `napplet` is missing, tell the user to install the standalone CLI — do not pretend the commands ran. Use manual wiring only for an explicit retrofit into an existing app, mirroring the boilerplate's shape.

If the project has a legacy `.napplet/config.json`, do not run a command that
consumes it until the user approves migration. The CLI asks interactively and
keeps the original bytes in `config.json.bak`; noninteractive use requires
explicit authorization via `--migrate-config`. It stops rather than replacing
an existing YAML or backup file. See `napplet-make` for the consent-first
workflow.

Keep these scripts as generated:

```jsonc
{ "scripts": { "build": "vite build", "type-check": "tsc --noEmit", "verify": "pnpm test:guidance && pnpm type-check && pnpm build", "test:conformance": "pnpm build && napplet-conformance ./dist" } }
```

## Step 2 — Project-specific edit points

| File | Edit |
| --- | --- |
| `.napplet/config.yaml` | Read-only for you; CLI-owned deployment metadata |
| `vite.config.ts` | Hard `requires: [...]`, optional integrations in `optional: [...]`, `archetypes`, keep `artifactMode: 'single-file'` and the `nappletType` fallback |
| `index.html` | Keep `<title>`, `<meta viewport>`, `#app` root. **Delete the starter `masthead` / `eyebrow` / `<h1>`** and the demo panels; add only the product's markup (`napplet-ui` Rule 1) |
| `src/styles.css` | Replace the starter's page layout (`.app-shell { padding: 2rem }`, `.workspace { width: min(1040px, 100%) }`, `body { min-width: 320px }`) with the compact, full-frame, container-query layout from `napplet-ui` |
| `src/main.ts` | Product behavior; SDK-first calls; keep `domain-availability.ts`'s `runtimeHasDomain` pattern for optional-domain gating |
| `tests/guidance.test.mjs` | The template's own guard runs under `pnpm verify`. It encodes *demo* expectations (starter control ids, no `requires:` in `vite.config.ts`, the `.codex/skills/README.md` pointer). When you replace the demo, update those product-specific lines to your product — keep the script, the forbidden-surface scans, and the OUTBOX-first assertions |
| `README.md`, `docs/*` | Product usage, NAP boundaries, verification notes |

`package.json`: rename the package; add dependencies only when the feature truly needs them, and prove they carry no dormant network/storage paths into the bundle.

## Step 3 — Manifest configuration

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import { nip5aManifest } from '@napplet/vite-plugin';

export default defineConfig({
  build: { modulePreload: { polyfill: false } },
  plugins: [
    nip5aManifest({
      description: 'Describe the napplet purpose in plain text',
      nappletType: 'my-napplet',        // build-local fallback; deploy metadata comes from napplet init
      artifactMode: 'single-file',      // fold assets, keep inline scripts, one index.html
      requires: ['outbox', 'storage'],  // hard requirements only, bare domain names
      optional: ['theme'],      // integrations with a usable fallback
      // archetypes: [{ slug: 'note', convention: 'napplet:note/open' }],  // see napplet-interop
    }),
  ],
});
```

Keep both capability lists aligned with the design and the SDK domains actually used. A guarded call still needs its optional declaration; importing an SDK wrapper or checking presence does not by itself populate deployment metadata. Current tooling emits `R`/`O` tags. If a constrained generation service only accepts application source, use its documented data-only metadata surface; flag a missing surface rather than silently omitting declarations or editing protected build configuration.

The artifact hash lands in `.nip5a-manifest.json` and the signed event, not in a meta tag. `VITE_DEV_PRIVKEY_HEX` produces a signed manifest in CI; dev builds work without it.

## Step 4 — Implement

1. **Shell first, then features.** Lay out `index.html` + `styles.css` per `napplet-ui`: full-frame root, compact tokens, tier rules, theme application, inline states, no title header. Check it at `200×160` and `2400×1200` before wiring data.
2. **Calls are SDK-first.** `import { outbox, storage, identity, … } from '@napplet/sdk'`; `window.napplet?.domain` only decides whether an optional feature renders. Exact signatures: `napplet-sdk` and the installed `@napplet/sdk` types.
3. **Boundaries from the spec.** Social reads/publishes through `outbox`; social actions through `common` / `lists` / `count` / `dm`; `relay` only where the spec names the escape hatch, with a code comment stating it.
5. **Teardown.** Close every subscription and revoke object URLs.
6. **States.** Signed-out (`identity.getPublicKey()` returns `""`), optional domain absent, publish failure (`result.ok === false`), resource rejection `code` — each renders a compact inline state, never a blank frame.

## Step 5 — Validate the generated project

```bash
pnpm verify              # guidance test + type-check + single-file build
pnpm test:conformance    # real Chromium + reference shell against ./dist
```

Then the `napplet-ui` four-frame check and the `napplet-test` boundary audit. For a retrofit, add equivalent scripts and run the same commands.

## Step 6 — Preview through Paja, not Vite

```bash
napplet paja -- pnpm vite --host 127.0.0.1
```

Report the URL Paja prints. A raw Vite URL is an asset server without a runtime — never present it as a napplet preview. If `napplet` or the configured Kehto/Paja binary is missing, say so and rely on conformance for automated verification.

## Common pitfalls

- Leaving the starter masthead, eyebrow, or `<h1>` in place, or shipping the starter's centered 1040px column — see `napplet-ui`.
- Only checking one desktop width — the napplet is resized live; check four frames.
- Recreating the boilerplate by hand, or importing `@napplet/shim` in napplet code — the runtime injects `window.napplet`.
- Treating open NAP proposals as shipped APIs, or gating unrelated domains on optional `shell.ready()`.
- `relay` as the default data layer; hand-built social events instead of `common` / `lists`.
- `localStorage`, `fetch`, `<img src=https://…>`, `WebSocket`, `window.nostr` — none exist in the sandbox.
- External `<script src>` in the artifact — JS must be inline; `artifactMode: 'single-file'` handles it.
- Trusting upstream `Content-Type` for resource bytes — the shell delivers a byte-sniffed `mime`.
