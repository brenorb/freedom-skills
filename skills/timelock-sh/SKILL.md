---
name: timelock-sh
description: Use this skill when the user wants to time-lock a local file with timelock.sh so it can only be decrypted after a specific UTC minute, or when you need to inspect, decrypt, or troubleshoot a timelock.sh CMS `.enc` file from the command line without an SDK or account.
---

# timelock-sh

Use the bundled wrapper around `timelock.sh` and local OpenSSL 3.x to encrypt a file for release at a future UTC minute, inspect the embedded unlock timestamp, or decrypt once the key is public.

## Default workflow

1. Encrypt with the bundled wrapper:

```bash
python3 skills/timelock-sh/scripts/timelock.py encrypt \
  --unlock 2026-07-01T12:00Z \
  --input /absolute/path/to/plaintext.txt
```

2. For non-text payloads such as archives, images, or other opaque files, use the same wrapper flow. The wrapper already adds the required OpenSSL `-binary` mode:

```bash
python3 skills/timelock-sh/scripts/timelock.py encrypt \
  --unlock 2026-07-01T12:00Z \
  --input /absolute/path/to/archive.tar.gz
```

3. Read the JSON result:
- `unlock_minute` is normalized to UTC minute form `YYYY-MM-DDTHH:MMZ`.
- `output_path` is the generated CMS ciphertext, defaulting to `<input>.enc`.

4. If the user wants to inspect an existing ciphertext before decrypting it, extract the embedded unlock minute:

```bash
python3 skills/timelock-sh/scripts/timelock.py extract-minute \
  --input /absolute/path/to/plaintext.txt.enc
```

5. Decrypt after release:

```bash
python3 skills/timelock-sh/scripts/timelock.py decrypt \
  --input /absolute/path/to/plaintext.txt.enc
```

6. If the key is not public yet, the wrapper returns a structured `425` error with `retry_after_seconds`. Use that instead of retrying blindly.
7. If the user wants raw `curl` or `openssl` patterns, service limits, or error semantics, read `references/commands.md`.
8. If the encrypted file will be sent to a non-technical recipient or to someone without this skill, ask whether they also want one or both of these handoff artifacts:
- A plain-text instruction document that points the recipient to `https://timelock.sh` and explains the manual browser flow step by step.
- A simple one-shot decrypt script with the encrypted filename already filled in, so the recipient can run it without editing configuration first.

## Defaults

- Prefer the bundled wrapper over handwritten `curl` plus `openssl` assembly because the OAEP flags and timestamp handling are easy to get wrong.
- Prefer `YYYY-MM-DDTHH:MMZ` for user-facing timestamps and normalize other accepted input to that form.
- Prefer letting the wrapper extract the unlock minute from the ciphertext instead of asking the user to supply it again during decrypt.
- Prefer JSON output from the wrapper so downstream automation can inspect paths, minutes, and retry hints deterministically.

## Safety rules

- Treat this as an external network action against the public `https://timelock.sh` API.
- Call out that plaintext stays local during encryption; only the public certificate or released private key is fetched from the service.
- Call out that once the unlock minute arrives, the decryption key is public forever. This is time-locking, not recipient-restricted encryption.
- Do not describe a ciphertext as private after release time unless there is a separate confidentiality layer.
- Do not promise sub-minute scheduling. timelock.sh is UTC and minute-granular only.

## Gotchas

- OpenSSL 3.x is required for the AES-256-GCM plus RSA-OAEP CMS flow used by timelock.sh.
- The two `-keyopt` flags are required for compatibility with timelock.sh decryptors.
- `-binary` is required for non-text payloads such as archives, images, and other opaque files.
- Certificates are only available up to roughly 30 days ahead. Far-future encrypt attempts should fail before encryption starts.
- Keys requested before release return `425 Too Early` and may include a `Retry-After` header.
- The wrapper defaults the decrypt output to the original filename when the input ends with `.enc`; otherwise it writes `<input>.decrypted`.
