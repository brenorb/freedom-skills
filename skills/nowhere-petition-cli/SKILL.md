---
name: nowhere-petition-cli
description: "Create, update, inspect, sign, encrypt, and operate Nowhere petition pages with the local `nowhere` CLI. Use when the user wants a petition fragment or URL, needs to publish signatures with an existing Nostr key or anonymously, or needs the owner-only signature review flows without using hostednowhere.com."
---

# nowhere-petition-cli

Start with the `nowhere` subcommand that directly matches the request. Prefer `--json` for agent workflows.

## Core Commands

- Create: `nowhere create petition --input petition.json --json`
- Update: `nowhere update <petition-fragment-or-url> --patch patch.json --json`
- Inspect or verify:
  - `nowhere inspect <petition> --json`
  - `nowhere verify <petition> --json`
- Sign or encrypt only when requested:
  - `nowhere sign <petition> --secret nsec1... --json`
  - `nowhere encrypt <petition> --password ...`
  - `nowhere decrypt <petition> --password ...`
- Petition relay flows:
  - `nowhere petition sign <petition> --input signature.json --secret nsec1... --json`
  - `nowhere petition count <petition> --json`
  - `nowhere petition signatures <petition> --secret nsec1... --json`

## Workflow

1. Build the petition with `create petition` or revise it with `update`.
2. Confirm the fragment decodes as `petition` with `inspect`.
3. Use `petition sign` to publish signer data. Omit `--secret` only when the task explicitly wants anonymous signing.
4. Use `petition count` for public progress and `petition signatures` only when the owner secret is available and the task needs the decrypted signer list.

## Inputs To Prepare

- `petition.json`: upstream Nowhere petition codec shape
- `patch.json`: partial petition object for `update`
- `signature.json`: signer payload expected by the petition flow

## Sharp Edges

- Petition sites are owner-key-sensitive. Without the real owner key, you cannot later decrypt signer data with `petition signatures`.
- `petition sign` now enforces the petition's own required signer fields and country restrictions before publishing.
- `petition signatures` is owner-only because the website encrypts signer payloads to the petition pubkey.

