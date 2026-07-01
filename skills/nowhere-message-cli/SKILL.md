---
name: nowhere-message-cli
description: "Create, update, inspect, sign, encrypt, and verify Nowhere message pages with the local `nowhere` CLI. Use when the user wants a message fragment or URL, especially for programmable creation or revision without opening the Hosted Nowhere builder."
---

# nowhere-message-cli

Start with the exact `nowhere` command that matches the request. Prefer `--json` for agent workflows.

## Core Commands

- Create: `nowhere create message --input message.json --json`
- Update: `nowhere update <message-fragment-or-url> --patch patch.json --json`
- Inspect: `nowhere inspect <message> --json`
- Sign: `nowhere sign <message> --secret nsec1... --json`
- Verify: `nowhere verify <message> --json`
- Encrypt or decrypt when requested:
  - `nowhere encrypt <message> --password ...`
  - `nowhere decrypt <message> --password ...`

## Workflow

1. Assemble the upstream message payload.
2. Run `create message` for a new page or `update` for an existing fragment.
3. Sign only when the user needs stable authorship tied to a real Nostr key.
4. Use `inspect` or `verify` to confirm the fragment decodes as `message`.

## Input Shape

- `message.json`: builder payload with fields such as `name`, `description`, `image`, `pubkey`, and `tags`
- `patch.json`: partial object to merge into an existing message page

## Sharp Edges

- Message pages are builder-only in the CLI today. There is no relay-backed inbox or reply flow for `message`.
- Signing and encryption remain separate operations. Do not assume a signed page is encrypted or vice versa.

