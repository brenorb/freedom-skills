---
name: croc
description: Send or receive files and folders between two computers with croc's encrypted live transfer and one-time code, including non-interactive agent workflows. Use when both endpoints can stay online until the transfer finishes.
compatibility: Requires Python 3 and the Croc CLI; the non-interactive helper is tested with Croc v11.6.6 on Linux and macOS. Network access is needed for live transfers.
metadata:
  version: "0.1.0"
  repository: "https://github.com/schollz/croc"
---

# Croc

## Local configuration

<!-- croc-config:start -->
Model may handle transfer links and codes: not configured
<!-- croc-config:end -->

Read this section from the installed `SKILL.md` on every invocation, including in a new chat. If it says `not configured`, ask whether transfer links/codes may pass through this model and its chat/tool history, or must stay outside the model. After the user's answer, edit the line above in this very file to `allowed` or `private`, and reread it to verify. If the current request already explicitly answers that question, save the choice directly. Apply a configured choice without asking again. Change it only when the user requests it; to reset, edit it back to `not configured`. There is no time limit or separate settings file. See [the configuration behavior](references/local-privacy.md). This preference does not authorize sending files.

## Send

With the file and recipient authorized and the privacy choice configured, run the bundled helper:

```bash
python3 scripts/transfer.py send "/absolute/path/to/file"
```

Pass multiple approved paths as separate arguments. In **allowed** mode, the sender generates a fresh code if needed and returns it in the `running` JSON event; deliver it only to the authorized recipient. In **private** mode, provision the same `CROC_SECRET` locally on both endpoints and keep it outside model/tool output. The helper requires Python 3 and croc, needs no TTY or stdin, and uses `--yes --ignore-stdin --disable-clipboard --no-update-check`. It discards raw Croc output and terminates Croc after a total deadline (600 seconds by default; put `--timeout 3600` before `send` for one hour). Read [automation](references/automation.md) and [trust assumptions](references/trust-assumptions.md) for the selected mode.

Prefer explicit files. For a folder, inspect hidden files and metadata or stage a clean copy containing only approved files: croc v11.6.6 includes `.git` by default. Do not transfer credential material such as wallet seeds or private keys.

Keep the sender running while the recipient connects. In private mode without local secret provisioning, use a private human terminal outside the agent transcript: `croc --ignore-stdin --disable-clipboard send -- "/absolute/path/to/file"`. Retrieve its generated code there and deliver it through an authorized private channel. In either mode, avoid persistent logs and command-line secrets. If an invite escapes the chosen boundary, stop the sender and generate a fresh code.

## Receive

With receiving authorized, the expected sender/files established, the policy configured and the sender's `CROC_SECRET` set in the receiver environment, receive into an existing empty directory:

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
