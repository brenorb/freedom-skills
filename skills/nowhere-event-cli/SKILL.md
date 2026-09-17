---
name: nowhere-event-cli
description: "Create, update, inspect, sign, encrypt, and verify Nowhere event pages with the local `nowhere` CLI. Use when the user wants a poster-style event fragment or URL without opening the Hosted Nowhere builder."
---

# nowhere-event-cli

Start with the exact `nowhere` command that matches the task. Prefer `--json` for agent workflows.

## Core Commands

- Create: `nowhere create event --input event.json --json`
- Update: `nowhere update <event-fragment-or-url> --patch patch.json --json`
- Inspect: `nowhere inspect <event> --json`
- Sign: `nowhere sign <event> --secret nsec1... --json`
- Verify: `nowhere verify <event> --json`
- Encrypt or decrypt when requested:
  - `nowhere encrypt <event> --password ...`
  - `nowhere decrypt <event> --password ...`

## Workflow

1. Build the event payload in upstream Nowhere codec shape.
2. Run `create event` for a new page or `update` for an existing one.
3. If the event should have author provenance, sign it with the real event owner's key.
4. Use `inspect` or `verify` to confirm the fragment decodes as `event` and the signature state matches the request.

## Input Shape

- `event.json`: event builder payload with fields such as `name`, `description`, `image`, `pubkey`, and `tags`
- `patch.json`: partial object to merge into an existing event before re-encoding

## Sharp Edges

- `create event` only builds the fragment; it does not publish anything to relays.
- Signing and encryption are separate actions. Do not assume one implies the other.
- Use a real key only when the user wants long-term authorship or verification. Skip signing for disposable mocks unless asked.
