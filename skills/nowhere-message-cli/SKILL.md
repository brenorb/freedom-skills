---
name: nowhere-message-cli
description: "Create, update, inspect, sign, encrypt, verify, and tip Nowhere message pages with the local `nowhere` CLI. Use when the user wants a message fragment or URL, or needs to inspect message tip methods or mint a Lightning tip invoice without opening the Hosted Nowhere builder."
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
- Tip helpers:
  - `nowhere message tip methods <message> --json`
  - `nowhere message tip invoice <message> --sats 2100 --json`

## Workflow

1. Assemble the upstream message payload.
2. Run `create message` for a new page or `update` for an existing fragment.
3. Sign only when the user needs stable authorship tied to a real Nostr key.
4. If the message includes tag `l`, use `message tip methods` to inspect reader payment options and `message tip invoice` only when the task explicitly needs a live Lightning invoice.
5. Use `inspect` or `verify` to confirm the fragment decodes as `message`.

## Input Shape

- `message.json`: builder payload with fields such as `name`, `description`, `image`, `pubkey`, and `tags`
- `patch.json`: partial object to merge into an existing message page

## Sharp Edges

- Message pages still do not have a relay-backed inbox or reply flow in the CLI.
- `message tip invoice` only works for the Lightning entry encoded in tag `l`. Custom tip methods are list/copy flows.
- Signing and encryption remain separate operations. Do not assume a signed page is encrypted or vice versa.
