---
name: hosted-nowhere
description: Create, update, inspect, and operate Nowhere message, drop, event, fundraiser, petition, forum, and SVG art pages using nowhere-cli through npx or Hosted Nowhere builders. Includes deprecated Store workflows for experiments and existing stores.
metadata:
  version: "0.1.0"
  repository: "https://github.com/brenorb/nowhere-cli"
  homepage: "https://hostednowhere.com"
  compatibility: "CLI workflows require Node.js 20+ and npx; no global CLI install is needed. First use may download nowhere-cli from npm. Browser workflows require a browser; relay operations and payment-service helpers require network access."
---

# Hosted Nowhere

Start with the action the user requested. For example:

```sh
npx --yes nowhere-cli create message --input message.json --json
npx --yes nowhere-cli update "$SITE_URL" --patch patch.json --json
npx --yes nowhere-cli inspect "$SITE_URL" --json
```

Use `npx --yes nowhere-cli <command>` directly; npm runs the package's `nowhere`
executable without a global install. The first run downloads the package if it is
not cached. Do not start with an installation check or install it globally.

For creation, prepare the input from the selected app reference first. For an
existing URL whose type is unknown, inspect it first. Prefer the CLI for structured
work; use the browser when requested or when a visual builder is needed.
Read only the selected app reference and any shared reference needed for the task.
Paths below are relative to this skill directory, not the user's working directory.

## Route to the app

| User wants | App reference |
| --- | --- |
| Letter, announcement, message page, reader tips | [Message](references/message.md) |
| Plain text, notes, code, or a text drop | [Drop](references/drop.md) |
| Event poster or invitation | [Event](references/event.md) |
| Donation page or donation methods/invoices | [Fundraiser](references/fundraiser.md) |
| Petition, signing, counts, owner review/export | [Petition](references/petition.md) |
| Discussion, replies, torrents, chat, private rooms | [Forum](references/forum.md) |
| SVG artwork in a link | [Art](references/art.md) |
| Existing store or an explicit store experiment | [Store — deprecated](references/store.md) |

`inspect` calls a forum's decoded site type `discussion`; its command is `forum`.
Choose by the intended outcome, not just a keyword: a message page is different
from a forum chat message. Do not invent inbox/reply support for static apps.

## Shared CLI operations

```sh
npx --yes nowhere-cli create <app> --input input.json --json
npx --yes nowhere-cli update "$SITE_URL" --patch patch.json --json
npx --yes nowhere-cli inspect "$SITE_URL" --json
npx --yes nowhere-cli verify "$SITE_URL" --json
```

JSON tags use objects such as `{"key":"t","value":"Title"}`; boolean tags use
`null` values. Optional `pubkey` accepts npub, hex, or Nowhere base64url. Petition,
forum, and Store need the intended owner's public key. The example owner key in
the bundled fixtures is public test data; replace it for real use.

Updates merge object fields, **replace entire arrays** (including `tags` and
`items`), and remove fields patched to `null`. Build narrow patches so unrelated
content survives. Before replacing arrays, review the existing entries: `inspect`
returns a summary, not the full editable payload. Use the browser's import/preview
when the original payload is unavailable.

Creation/update builds a new URL; it does not edit already distributed links or
publish relay activity. Preserve the old link and return the new one. For forum,
petition, and legacy Store changes, read the app's namespace cautions first.
When a relay is supplied, pass `--relay` explicitly on every runtime read/write;
do not assume an encoded relay tag overrides the CLI's defaults. This flag belongs
to app runtime commands such as `petition sign` and `forum posts`. Local URL
commands (`create`, `update`, `inspect`, `verify`, `sign`, `encrypt`, `decrypt`)
do not accept `--relay`.

Signing and encryption are separate optional operations. Preserve the protections
required by the task: `update` does **not** automatically retain either one.
For protected links, owner keys, or a remote signer, read
[protection and final verification](references/verification.md).

## Browser path

Open `https://hostednowhere.com/create/<app>` and follow the selected app's
reference plus [browser workflow](references/browser.md). Inspect the live UI;
use field names and validation messages instead of fixed step numbers.

## Gotchas and completion

- **Store is deprecated:** public relays need not retain stock or orders; a buyer
  can pay without the seller reliably receiving the order. Hosted Nowhere removed
  it from the tool list and keeps it as a demonstration, unsuitable for a live
  shop. Explain this when routing a Store request; retain its legacy workflows.
  Source: [Hosted Nowhere's Store explanation](https://hostednowhere.com/store).
- The full fragment after `#` is the site. Preserve it exactly and quote URLs in
  shell commands. An unencrypted link exposes its content to anyone possessing it.
- Open the **final** link after all edits, signing, and encryption. Confirm the
  app, requested content, and protection state before delivering it. Follow the
  [completion checks](references/verification.md#completion-checks).
- Save requested artifacts with their requested names and formats. If command
  JSON is requested, capture the actual CLI output; a handwritten verification
  note is a separate artifact. Verification phrases do not prove a signature.
- Capture relay-write and invoice responses to a file in their original
  invocation (`--json > response.json`). Read that file afterward; do not repeat
  a write to recapture its output. Keep input and output filenames distinct so
  shell redirection does not truncate the input before the CLI reads it.
- Relay writes can have ambiguous outcomes. Follow
  [failure and retry guidance](references/troubleshooting.md) before retrying a
  publish. Missing commands, malformed input, unavailable relays, and partial
  decryption each need a different recovery.

CLI dependency: [`brenorb/nowhere-cli`](https://github.com/brenorb/nowhere-cli),
npm package `nowhere-cli`, executable `nowhere`, invoked through `npx`. Fixtures
and automated checks target version **0.3.0**; reproduce that baseline with
`npx --yes nowhere-cli@0.3.0 <command>`. Use targeted `--help` on a compatibility
error; see troubleshooting only when an action fails.

Sources: [Hosted Nowhere](https://hostednowhere.com),
[architecture](https://hostednowhere.com/how-it-works),
[upstream codec/web](https://github.com/5t34k/nowhere).
