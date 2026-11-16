---
name: hyperbeam
description: Use this skill when the user wants a quick 1:1 encrypted byte stream over HyperDHT or Hyperswarm via `hyperbeam`, especially for one-shot text streaming, binary file transfer, tarball transfer, or reconnecting to the same shared passphrase after a restart.
---

# hyperbeam

Use the local `hyperbeam` CLI as a raw 1:1 encrypted stdin/stdout pipe.

## Default workflow

1. If this machine is sending data, follow the send workflow.

For a one-shot text or stdout stream:

```bash
echo 'hello world' | hyperbeam
```

For a single file:

```bash
cat /absolute/path/to/file.bin | hyperbeam
```

For a directory or many files:

```bash
tar czf - /absolute/path/to/folder | hyperbeam
```

Each sending command prints a passphrase on stderr. Share that passphrase with the receiving peer and tell them what kind of byte stream you are sending: plain stdout, a single file, or a tarball.

2. If this machine is receiving data, follow the receive workflow.

For a plain stdout stream:

```bash
hyperbeam <passphrase>
```

For a single file:

```bash
hyperbeam <passphrase> > /absolute/path/to/file.bin
```

For a tarball stream:

```bash
hyperbeam <passphrase> | tar xzf -
```

3. If the listening side must come back with the same passphrase after a restart, reuse the phrase in announce mode:

```bash
hyperbeam <passphrase> -r
```

4. Only fall back to setup checks or onboarding when the first useful command fails because `hyperbeam` is missing or the local environment is uncertain. In that case:

```bash
command -v hyperbeam
hyperbeam --help
```

Then read `references/onboarding.md`.

5. If the user needs raw command patterns beyond the defaults here, read `references/commands.md`.

## Defaults

- Treat Hyperbeam as a raw encrypted byte pipe, not as a filesystem sync tool, Git remote, or multiplexed session manager.
- Prefer one-shot transfers where one side produces bytes and the other side captures them immediately.
- Prefer `cat ... | hyperbeam` and `hyperbeam ... > file` for single files because the data model is only bytes, not filenames.
- Prefer `tar` streaming for folders or multi-file handoff.
- Prefer action first. Do not front-load setup checks once `hyperbeam` is already verified in the current environment.

## Safety rules

- Treat the passphrase as a bearer secret. Anyone with it can connect to that beam.
- Confirm before sending sensitive data or sharing a passphrase outside the machine.
- Treat this as an external network action.
- Keep stdout clean for payload bytes only. Status messages belong on stderr; do not add extra stdout text around the pipe.
- Confirm the receiver path before overwriting files with `>`.

## Gotchas

- Hyperbeam is 1:1 and byte-oriented only. It does not preserve filenames, directories, timestamps, or metadata by itself.
- EOF matters. When the sender command finishes and closes stdout, the beam ends.
- There is no built-in resume, checkpointing, or multi-file session protocol.
- The generated passphrase is printed in status output. Be careful with shell history, logs, or copied terminal transcripts.
- The restart flag is positional in practice: use `hyperbeam <passphrase> -r`, not `hyperbeam -r <passphrase>`.
- Because the transport is raw stdin/stdout, using an interactive shell directly can mix terminal behavior with payload bytes. Prefer explicit pipelines and redirections.
