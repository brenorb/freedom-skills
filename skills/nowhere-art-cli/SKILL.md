---
name: nowhere-art-cli
description: "Create, update, inspect, sign, encrypt, and verify Nowhere art pages with the local `nowhere` CLI. Use when the user wants an art fragment or URL, including pages driven by inline SVG, without opening the Hosted Nowhere builder."
---

# nowhere-art-cli

Start with the exact `nowhere` command that matches the request. Prefer `--json` for agent workflows.

## Core Commands

- Create: `nowhere create art --input art.json --json`
- Update: `nowhere update <art-fragment-or-url> --patch patch.json --json`
- Inspect: `nowhere inspect <art> --json`
- Sign: `nowhere sign <art> --secret nsec1... --json`
- Verify: `nowhere verify <art> --json`
- Encrypt or decrypt when requested:
  - `nowhere encrypt <art> --password ...`
  - `nowhere decrypt <art> --password ...`

## Workflow

1. Build the art payload in upstream Nowhere codec shape.
2. Use `create art` for new work or `update` for an existing fragment.
3. Sign only when the art page should keep durable authorship metadata.
4. Use `inspect` or `verify` to confirm the fragment decodes as `art`.

## Input Shape

- `art.json`: builder payload with `name`, optional `svg`, optional `pubkey`, and `tags`
- `patch.json`: partial object to merge into an existing art page

## Sharp Edges

- Inline `svg` content is the art-specific field in the current CLI builder.
- Art pages are builder-only in the CLI today. There is no relay-backed publishing workflow for `art`.

