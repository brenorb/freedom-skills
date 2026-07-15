---
name: nowhere-drop-cli
description: "Create, update, inspect, sign, encrypt, and verify Nowhere drop pages with the local `nowhere` CLI. Use when the user wants a drop fragment or URL created or revised programmatically without opening the Hosted Nowhere builder."
---

# nowhere-drop-cli

Start with the exact `nowhere` command that matches the request. Prefer `--json` for agent workflows.

## Core Commands

- Create: `nowhere create drop --input drop.json --json`
- Update: `nowhere update <drop-fragment-or-url> --patch patch.json --json`
- Inspect: `nowhere inspect <drop> --json`
- Sign: `nowhere sign <drop> --secret nsec1... --json`
- Verify: `nowhere verify <drop> --json`
- Encrypt or decrypt when requested:
  - `nowhere encrypt <drop> --password ...`
  - `nowhere decrypt <drop> --password ...`

## Workflow

1. Build the upstream drop payload with the exact content the user wants to ship.
2. Use `create drop` for new work or `update` for an existing fragment.
3. Sign only when the drop should carry real author provenance.
4. Use `inspect` or `verify` to confirm the fragment decodes as `drop`.

## Input Shape

- `drop.json`: builder payload with `name`, `description`, optional `pubkey`, and `tags`
- `patch.json`: partial object to merge into an existing drop page

## Sharp Edges

- `description` is required in the current CLI builder for `drop`.
- Drop pages are builder-only in the CLI today. There is no relay-backed runtime for `drop`.

