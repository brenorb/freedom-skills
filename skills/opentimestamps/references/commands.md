# OpenTimestamps command patterns

Read this file only when the user needs raw `ots` commands, browser fallback steps, or operational details beyond the default wrapper workflow.

## Install the official client

Prefer an ephemeral install when `ots` is not already present:

```bash
uvx --from opentimestamps-client ots --help
```

For a persistent install:

```bash
pip3 install --user opentimestamps-client
```

## Stamp a local file

```bash
FILE=/absolute/path/to/document.pdf
ots stamp "${FILE}"
```

This writes `${FILE}.ots` next to the original file.

To pin custom calendars:

```bash
ots stamp \
  --calendar https://a.pool.opentimestamps.org \
  --calendar https://b.pool.opentimestamps.org \
  "${FILE}"
```

## Inspect an `.ots` proof

```bash
ots info /absolute/path/to/document.pdf.ots
```

Use this when the user wants the file digest, the attestation tree, or to check whether the proof is still pending.

## Upgrade a proof

```bash
ots upgrade /absolute/path/to/document.pdf.ots
```

Important behavior:

- Successful upgrades rewrite the timestamp and move the previous file to `.ots.bak`.
- `ots upgrade --dry-run ...` checks whether newer attestations are available without rewriting the file.

## Verify a proof

With the original file:

```bash
ots verify /absolute/path/to/document.pdf.ots
```

With an explicit file path:

```bash
ots verify -f /absolute/path/to/document.pdf /absolute/path/to/document.pdf.ots
```

With a digest instead of a file:

```bash
ots verify -d <hex_digest> /absolute/path/to/document.pdf.ots
```

If a local Bitcoin Core node is available, pin it explicitly:

```bash
ots --bitcoin-node http://user:pass@127.0.0.1:8332 verify /absolute/path/to/document.pdf.ots
```

## Browser fallback on opentimestamps.org

Use the website only when the user explicitly wants the browser flow or the CLI path is unavailable:

1. Open [opentimestamps.org](https://opentimestamps.org/).
2. Drop the file on "STAMP & VERIFY".
3. Download the generated `.ots` file and keep it beside the original file.
4. Later, return to the same page with both the original file and the `.ots` proof to verify it.

## Output patterns worth recognizing

- `Submitting to remote calendar ...`: a calendar accepted the stamp request.
- `Pending confirmation in Bitcoin blockchain`: the proof exists but is not yet complete enough to verify against a Bitcoin block.
- `Success! Bitcoin block ... attests data existed as of ...`: verification succeeded.

## Constraints and safety notes

- OpenTimestamps proves that a file digest existed by a certain time; it does not encrypt the file.
- The `.ots` proof is safe to share publicly only if the underlying file digest is not sensitive in context.
- Keep the original file unchanged after stamping. Verification fails if the file bytes differ.
- A freshly stamped proof is often incomplete. Expect to use `upgrade` later before verification succeeds.
