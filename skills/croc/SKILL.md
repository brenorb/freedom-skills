---
name: croc
description: Send or receive files and folders between two computers with croc's encrypted live transfer and one-time code, including non-interactive agent workflows. Use when both endpoints can stay online until the transfer finishes.
---

# Croc

## Send

With the file and recipient authorized and `CROC_SECRET` already provisioned locally on both endpoints, run the bundled helper (resolve `scripts/` relative to this skill):

```bash
python3 scripts/transfer.py send "/absolute/path/to/file"
```

Pass multiple approved paths as separate arguments. The helper requires Python 3 and croc, needs no TTY or stdin, and returns only JSON status. It uses `--yes --ignore-stdin --disable-clipboard --no-update-check`, discards Croc stdout and stderr, and terminates Croc after a total deadline (600 seconds by default; put `--timeout 3600` before `send` for one hour). Read [automation](references/automation.md) for secret provisioning, direct commands, and error handling, and [trust assumptions](references/trust-assumptions.md) before handling an invite.

Prefer explicit files. For a folder, inspect hidden files and metadata or stage a clean copy containing only approved files: croc v11.6.6 includes `.git` by default. Do not transfer credential material such as wallet seeds or private keys.

Keep the sender running while the recipient connects. If no shared secret has been provisioned, use a private human terminal outside the agent transcript: `croc --ignore-stdin --disable-clipboard send -- "/absolute/path/to/file"`. Retrieve its generated code there and deliver it only through an authorized private channel. Keep the invite and its receive URL out of command arguments and shared output. If it leaks, stop the sender and generate a fresh code.

## Receive

With receiving authorized, the expected sender/files established, and `CROC_SECRET` provisioned locally, receive into an existing empty directory:

```bash
python3 scripts/transfer.py receive "/absolute/path/to/receive-dir"
```

The helper refuses a nonempty destination and never enables overwrites. `--yes` replaces Croc's acceptance prompt after authorization; it does not validate the remote manifest before writing. Check resulting filenames, sizes and any expected hashes after completion. Treat received content as untrusted and don't open or execute it automatically. Existing authorization covers the operation; do not ask again just to remove CLI prompts.

For a human-operated transfer without a provisioned secret, use a private interactive Bash terminal and enter the code without echoing it or recording the literal in shell history:

```bash
cd -- "/absolute/path/to/receive-dir" &&
(
  read -r -s -p 'Croc code: ' code && printf '\n' &&
  CROC_SECRET="$code" croc
)
```

In this human-operated path, use Croc's interactive acceptance prompt. A displayed code, `running` status or a waiting sender does not mean the recipient received anything; require successful completion and verify the files.

## If the transfer stalls

- Both ends must be online together. Verify the sender is still running, both ends have the exact code, and any already-approved custom relay settings agree. Do not silently switch relays. If interrupted, keep partial data and consult the upstream resume instructions before restarting.
- Croc uses end-to-end encryption and can fall back to a relay. Encryption protects file contents in transit; it does not make network metadata invisible. Do not relay a transfer when the user requires a direct-only connection.
- If croc is missing, use the [official release](https://github.com/schollz/croc/releases/tag/v11.6.6) or the platform's trusted package manager within the user's setup authorization. See the [upstream usage and installation guide](https://github.com/schollz/croc/blob/v11.6.6/README.md) for other shells and options. This skill covers live file transfers, not `croc ssh` or hosted storage.
