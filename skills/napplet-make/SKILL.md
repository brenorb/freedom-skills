---
name: napplet-make
description: Use when a user asks to create, build, implement, prototype, or port a complete napplet (sandboxed Nostr iframe applet) in one prompt. Entry point that triages the project state and toolchain, then routes through napplet-port (if migrating), napplet-design, napplet-ui, napplet-build (+ napplet-sdk / napplet-interop as needed), and napplet-test, and ends with an evidence report. Keeps social reads and publishes OUTBOX-first and treats NAP-RELAY as an explicit escape hatch only.
compatibility: CLI workflows assume `@napplet/cli` 0.13.0; package versions are independent, so verify installed SDK types.
license: MIT
metadata:
  version: "0.2.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
  upstream_sha: "6c4dafd20142cade5a51ae049beecfef7c8f7c2e"
  upstream_cli: "0.13.0"
  upstream_sdk: "0.30.0"
  upstream_source: "https://github.com/napplet/web/tree/6c4dafd20142cade5a51ae049beecfef7c8f7c2e/skills/napplet-make"
---

# Making a Napplet End to End

Top-level workflow for "build me a napplet". Do not jump to code. The goal is a working, conformant, compact, any-size applet whose authority boundaries are right on the first pass.

Protocol truth: NIP-5D (<https://github.com/nostr-protocol/nips/pull/2303>) and the NAPs track (<https://github.com/napplet/naps>). Use only the surface shipped by the installed `@napplet/*` packages. Never invent message types, domains, manifest tags, loading rules, or shell authority to satisfy a prompt; a needed-but-undefined surface is a gap to report.

## Which skills, in which order

| Request | Route |
| --- | --- |
| New napplet from an idea | `napplet-design` → `napplet-ui` → `napplet-build` → `napplet-test` |
| Port an existing Nostr app / client / widget | `napplet-port` → `napplet-design` → `napplet-ui` → `napplet-build` → `napplet-test` |
| Add a feature to an existing napplet | Re-run `napplet-design` for that feature's boundary → `napplet-build` → `napplet-test` |
| Design, generate, or refine an app icon | `napplet-icon`; run `napplet-test` if integrating it into the app |
| Change only layout / visuals | `napplet-ui` → `napplet-test` (four-frame + theme checks) |
| Debug or verify a built napplet | `napplet-test`; edit only after reproducing the failure |
| Needs a NAP / domain the packages do not ship | Stop and flag the gap; do not fake it |

Load `napplet-sdk` while writing calls and `napplet-interop` only if the spec has cross-napplet features.

Use `napplet-icon` when the request includes an app icon or identity artwork. It owns the visual concept, image generation, refinement, and asset delivery; icon work is optional in the full build workflow.

## Step 1 — Start with the requested action

For a new napplet in the requested directory, start with the maintained
scaffold, then initialize its deployment metadata:

```bash
napplet create <directory>
cd <directory>
napplet init
```

For a port, first run `napplet-port` against the existing app, then create or
initialize the destination as appropriate. For an existing napplet, use the
requested specialized skill directly; do not scaffold over it. If the command
fails or the project state is genuinely unclear, use the fallback inspection
below. Do not make `command -v` or setup checks a mandatory first step.

## Step 2 — Brief

```
d-tag / deployment name:
new build or port:
single-purpose job (one line):
must-have flows:
optional flows:
form factor: compact applet; sizes it must survive; minimum (if any)
target runtime assumptions:
known protocol / package gaps:
```

Split a "whole app" request into focused napplets unless the user explicitly wants one compound napplet that still works in a small frame.

## Fallback — Inspect only when needed

When the direct action fails or the project state is uncertain, inspect the
directory and relevant tools:

```bash
pwd
command -v napplet || true
command -v kehto || command -v paja || true
test -f package.json && cat package.json
test -f .napplet/config.yaml && cat .napplet/config.yaml
test -f vite.config.ts && sed -n '1,120p' vite.config.ts
find . -maxdepth 2 -type f -not -path './node_modules/*' | sort | sed -n '1,120p'
```

If `.napplet/config.json` is present, preserve it and stop before running any
configuration-consuming CLI command. Explain that the current CLI migrates it
to `.napplet/config.yaml`, asks for consent in an interactive terminal, retains
the original bytes in `config.json.bak`, and removes the active JSON only after
YAML is written. Wait for the user's approval; do not add `--migrate-config`
without that approval. In noninteractive/CI use, migration is refused unless
the user explicitly authorized `--migrate-config`. Existing YAML or backup
files are conflicts: do not overwrite them. For the CLI's focused migration
cases, see its config migration tests in the upstream source recorded in this
skill's metadata.

| State | Action |
| --- | --- |
| `napplet` CLI unavailable | Tell the user to install the standalone CLI (or use the repo's documented local path). Never pretend `create` / `init` / `paja` ran. |
| Empty directory | `napplet create <dir>`, `cd`, `napplet init`. |
| Fresh boilerplate, no product work | Keep the substrate; run `napplet init` if metadata is absent; implement the product. |
| Initialized napplet (`.napplet/config.yaml` + generated scripts) | Inspect metadata and scripts; edit product surfaces only. |
| Brownfield app built on the boilerplate | Preserve compatible scripts/config; port only app code; do not re-scaffold. |
| Brownfield app without the boilerplate | `napplet-port` first, then add only the equivalent build / single-file / metadata / conformance wiring; document the retrofit. |

If Kehto/Paja is unavailable, continue build and conformance work and report the missing runtime as an open manual-preview gap. Never present a raw Vite URL as a napplet preview.

## Step 3 — Non-negotiables while executing

- **Sandbox authority.** No `fetch`, XHR, WebSocket, browser storage, cookies, `window.nostr`, external scripts/styles/images, relay pools, or signing in napplet code. Bytes → bundled or `resource`; state → `storage`; Nostr → `outbox` / `common` / `lists` / `count` / `dm`; links → `link`; `relay` only for a named relay-local escape hatch recorded in the brief.
- **Applet, not website.** No title header / tagline; compact density; fills the frame; good at tiny and huge sizes; declared minimum only when the UI truly breaks (`napplet-ui`).
- **SDK-first.** `@napplet/sdk` wrappers for calls; `window.napplet?.domain` only for optional-domain gating. Domain object presence is the availability signal; optional shell environment APIs do not gate other domains.
- **Keyboard controls.** Keep essential actions reachable through ordinary UI controls.
- **Requires = hard only.** Bare domain names; `theme`, `notify`, `resource`, `inc`, `intent` almost never belong there.
- **Theme covers the whole surface**, including `html` / `body` / root backgrounds, in dark and light.

## Step 4 — Definition of done

"Done" means all of these, with evidence in the final report:

- `pnpm verify` and `pnpm test:conformance` pass in the project (or the retrofit equivalents).
- Boundary audit from `napplet-test` is clean; every `relay` use has a written reason.
- `napplet-ui` four-frame check (`200×160`, `320×560`, `900×600`, largest available) in dark and light: no title header, no overflow, frame filled, minimum notice correct if declared.
- Manifest `requires` matches the spec's hard list; `.napplet/config.yaml` still owns deployment metadata.
- Paja preview URL reported, or Paja explicitly reported unavailable.
- Any protocol/package gap listed as a gap, not papered over.

Report: changed files, NAP domains used and why, relay escape hatches, frames and themes checked, commands run with results, untested gaps.
