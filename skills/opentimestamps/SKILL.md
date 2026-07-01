---
name: opentimestamps
description: Use this skill when the user wants to timestamp a local file with OpenTimestamps or opentimestamps.org, generate or inspect a `.ots` proof, upgrade a pending proof, or verify that a file digest was attested in Bitcoin from the command line or the public website.
---

# OpenTimestamps

Use the bundled wrapper around the official OpenTimestamps client to stamp local files, inspect `.ots` proofs, upgrade them when remote calendars have new attestations, and verify them against Bitcoin-backed timestamps.

## Default workflow

1. Stamp the local file with the bundled wrapper:

```bash
python3 skills/opentimestamps/scripts/opentimestamps.py stamp \
  --input /absolute/path/to/document.pdf
```

2. Read the JSON result:
- `timestamp_path` is the generated `.ots` proof, defaulting to `<input>.ots`.
- `submitted_calendars` lists the remote calendars that accepted the proof request.

3. If the user wants to inspect the proof tree or confirm whether it is still pending, inspect it:

```bash
python3 skills/opentimestamps/scripts/opentimestamps.py info \
  --timestamp /absolute/path/to/document.pdf.ots
```

4. If verification fails because the proof is still waiting on Bitcoin confirmation, upgrade it later:

```bash
python3 skills/opentimestamps/scripts/opentimestamps.py upgrade \
  --timestamp /absolute/path/to/document.pdf.ots
```

5. Verify once the proof is complete:

```bash
python3 skills/opentimestamps/scripts/opentimestamps.py verify \
  --timestamp /absolute/path/to/document.pdf.ots
```

6. If the original file is not next to the `.ots` proof, pass it explicitly:

```bash
python3 skills/opentimestamps/scripts/opentimestamps.py verify \
  --timestamp /absolute/path/to/document.pdf.ots \
  --input /absolute/path/to/document.pdf
```

7. If the user needs raw `ots` commands, browser instructions, or Bitcoin-node-specific details, read `references/commands.md`.

## Defaults

- Prefer the bundled wrapper over raw `ots` calls because it returns structured JSON and falls back to `uvx --from opentimestamps-client ots` when a persistent `ots` install is missing.
- Prefer storing the `.ots` file beside the original file and keeping the bytes unchanged after stamping.
- Prefer trying `verify` first; if it reports pending confirmations, run `upgrade` and retry instead of assuming the proof is broken.
- Prefer explicit `--input` on verify when the original file moved or was renamed.

## Safety rules

- Treat stamping and upgrading as external network actions because they contact public OpenTimestamps calendars.
- Call out that OpenTimestamps proves existence time for a digest; it does not encrypt the file or hide its contents.
- Do not claim a proof is complete until `verify` succeeds against a Bitcoin block.
- Do not modify the original file after stamping if the user expects later verification to succeed.
- Do not recommend sharing `.ots` files casually when the fact that a specific digest exists could itself be sensitive.

## Gotchas

- Freshly stamped proofs are often incomplete and may need one or more later `upgrade` passes before verification succeeds.
- Successful `upgrade` rewrites the timestamp and saves the old version as `.ots.bak`.
- `verify` can infer the original file when the `.ots` file still lives beside it with the original filename, but that inference breaks after renames or moves.
- If the user has a trusted local Bitcoin node, pass `--bitcoin-node` through the wrapper for stronger verification semantics.
- The website at `opentimestamps.org` is a valid fallback, but the CLI flow is easier to automate and audit.
