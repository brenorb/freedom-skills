---
name: nowhere-fundraiser-cli
description: "Create, update, inspect, sign, encrypt, and operate Nowhere fundraiser pages with the local `nowhere` CLI. Use when the user wants a fundraiser fragment or URL, wants to inspect donation methods, or needs a Lightning donation invoice from a fundraiser without using hostednowhere.com."
---

# nowhere-fundraiser-cli

Start with the `nowhere` command that directly matches the request. Prefer `--json` for agent workflows.

## Core Commands

- Create: `nowhere create fundraiser --input fundraiser.json --json`
- Update: `nowhere update <fundraiser-fragment-or-url> --patch patch.json --json`
- Inspect: `nowhere inspect <fundraiser> --json`
- Sign or verify:
  - `nowhere sign <fundraiser> --secret nsec1... --json`
  - `nowhere verify <fundraiser> --json`
- Encrypt or decrypt only when requested
- Donation helpers:
  - `nowhere fundraiser donate methods <fundraiser> --json`
  - `nowhere fundraiser donate invoice <fundraiser> --sats 5000 --json`

## Workflow

1. Build or revise the fundraiser with `create fundraiser` or `update`.
2. Inspect the fragment to confirm the site type is `fundraiser`.
3. If the user needs donation routing, list methods first with `fundraiser donate methods`.
4. Only request `fundraiser donate invoice` when the task explicitly needs a live Lightning invoice.

## Inputs To Prepare

- `fundraiser.json`: upstream Nowhere fundraiser codec shape
- `patch.json`: partial fundraiser object for `update`

## Sharp Edges

- Donation invoices only work for Lightning methods encoded in tag `l`.
- Custom donation handles are list/copy flows, not invoice-generation flows.
- Signing and encryption remain optional. Do not force them unless the user asked for them.
