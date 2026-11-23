---
name: croc
description: Send or receive files and folders between two computers with croc's encrypted live transfer and one-time code. Use when both endpoints can stay online until the transfer finishes.
---

# Croc

## Send

With the user's chosen file and recipient confirmed, start the live transfer:

```bash
croc send -- "/absolute/path/to/file"
```

Pass multiple approved paths as separate arguments. Prefer explicit files. For a folder, inspect hidden files and metadata or stage a clean copy containing only approved files: croc v11.6.6 includes `.git` by default. Do not transfer credential material such as wallet seeds or private keys.

Keep the sender running while the recipient connects. Use croc's generated code; anyone with it can attempt to join. Tell the user where to retrieve it locally or deliver it only to the intended recipient through an authorized private channel. Don't paste it into public posts, command arguments, logs, or shared transcripts. If it leaks, stop the sender and generate a fresh code.

## Receive

Confirm the expected sender and files. Receive into an empty directory (or the user's approved destination); do not accept unexpected filenames, file sizes, or overwrite prompts. In an interactive Bash terminal, enter the code locally without echoing it or recording the literal in shell history:

```bash
cd -- "/absolute/path/to/receive-dir" &&
(
  read -r -s -p 'Croc code: ' code && printf '\n' &&
  CROC_SECRET="$code" croc
)
```

Use croc's interactive acceptance prompt; don't use `--yes` or `--overwrite`. Treat received content as untrusted and don't open or execute it automatically. Confirm completion from the CLI and check the resulting files. A displayed code or a waiting sender does not mean the recipient received anything.

## If the transfer stalls

- Both ends must be online together. Verify the sender is still running, both ends have the exact code, and any already-approved custom relay settings agree. Do not silently switch relays. If interrupted, keep partial data and consult the upstream resume instructions before restarting.
- Croc uses end-to-end encryption and can fall back to a relay. Encryption protects file contents in transit; it does not make network metadata invisible. Do not relay a transfer when the user requires a direct-only connection.
- If croc is missing, use the [official release](https://github.com/schollz/croc/releases/tag/v11.6.6) or the platform's trusted package manager after approval. See the [upstream usage and installation guide](https://github.com/schollz/croc/blob/v11.6.6/README.md) for other shells and options. This skill covers live file transfers, not `croc ssh` or hosted storage.
