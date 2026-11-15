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

## Bounded operations and explicit waiting

The wrapper has a **120-second total execution budget** for each invocation. It includes starting `ots` (or `uvx`/`uv`), any capability probe and the operation itself. Set a longer finite budget only when the task calls for it:

```bash
python3 skills/opentimestamps/scripts/opentimestamps.py \
  --operation-timeout 900 --wait upgrade \
  --timestamp /absolute/path/to/document.pdf.ots
```

`--wait` asks the client to retry pending attestations until complete, but the wrapper still cancels it at the total deadline. Without `--wait`, the wrapper does not add retry rounds. On POSIX, cancellation kills the runner's process group, including client children started by `uvx`/`uv`; on other platforms only the immediate process is killed, so descendant cleanup remains unverified. Ctrl-C cancels the running client and returns exit code 130.

The operation deadline is separate from the optional **per-calendar** timeout:

```bash
python3 skills/opentimestamps/scripts/opentimestamps.py \
  --operation-timeout 60 verify \
  --timestamp /absolute/path/to/document.pdf.ots --timeout 5
```

`stamp --timeout` is supported by the released client. For `upgrade --timeout` and `verify --timeout`, the wrapper reads the selected client's subcommand help only when this option is requested. It forwards the option if advertised; otherwise it relies on the total deadline and reports `calendar_timeout_supported: false`. A `null` value means no calendar timeout was requested. Do not interpret the calendar timeout as a deadline for all calendars, startup, Bitcoin RPC or repeated `--wait` rounds.

A timeout returns JSON with `timed_out: true` and exit code **124**, distinct from the client's proof-validation failure. Any captured output is diagnostic only; no `verification` success is returned on timeout. Completion is unknown: a calendar submission may already have happened, and an upgrade may already have changed the proof/cache. Keep the original file, inspect `.ots`/`.ots.bak` if present, and do not blindly repeat submissions.

### Tested compatibility

- Released **opentimestamps-client v0.7.2**, tag `opentimestamps-client-v0.7.2`: verified its version, help, local `info`, invalid-proof errors and fallback behavior. Its upgrade/verify commands do **not** advertise `--timeout`.
- Reviewed upstream source at [`356195c69e09ff1c67528a8d25b18379d14845ed`](https://github.com/opentimestamps/opentimestamps-client/tree/356195c69e09ff1c67528a8d25b18379d14845ed). [`427a815`](https://github.com/opentimestamps/opentimestamps-client/commit/427a815548770c62f08124863cafe868ae56f06c) adds calendar deadlines to upgrade/verify; [`607fec3`](https://github.com/opentimestamps/opentimestamps-client/commit/607fec3720de7b41701493edd17171594b2cdb4b) fixes immediate retries on incomplete new attestations. These source changes must not be attributed to v0.7.2.
- Hermetic wrapper tests cover supported/unsupported help, stalled clients and probes, incomplete-attestation output, success/error parsing, bounded explicit waits and POSIX child cleanup. They do not establish live calendar behavior or validate an unreleased upstream installation. The wrapper uses the installed or package-resolved client; it does not silently replace it with upstream master.

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
