---
name: nostr-cli
description: "Use this skill when Codex needs to work with the local `nostr` command from xdamman/nostr-cli for non-interactive Nostr social and bot workflows: account setup, relay management, profile lookup, note posting, replies, DMs, follow graph changes, long-form NIP-23 publishing, or JSON/JSONL streaming for automations."
---

# nostr-cli

Use the local `nostr` binary as a terminal-first Nostr client for non-interactive social and bot workflows.

Leave interactive TUI flows out of scope unless the user explicitly asks for them.

## Default workflow

1. Check whether `nostr` is installed and whether any local account exists:

```bash
command -v nostr
nostr version --json
nostr accounts --json
```

2. If the binary is missing, or `nostr accounts --json` reports no account, read `references/onboarding.md`.
3. Before any write action, inspect the current account and relay state, then resolve the exact account that should be used:

```bash
nostr switch --json
nostr relays --json
```

4. For read-only work, use the CLI directly with machine-readable output:

```bash
nostr profile alice --json
nostr events --kinds 1 --since 1h --jsonl
nostr dm --watch --since 1h --jsonl
```

5. For DMs, public posting, replies, follows, or long-form publishing, prefer a dry run first when the command supports it, and pass `--account` explicitly for agent-initiated writes:

```bash
nostr dm alice "Hello" --account bot-account --json
nostr post "Hello Nostr" --account bot-account --dry-run --json
nostr reply note1abc... "Nice post" --account bot-account --dry-run --json
nostr post -f article.md --title "My Article" --account bot-account --dry-run --json
nostr follow alice --account bot-account --json
```

6. If the user needs raw command patterns beyond the defaults here, read `references/commands.md`.

## Defaults

- Prefer `nostr-cli` when the task is non-interactive Nostr usage: posts, replies, DMs, follows, profiles, account inspection, relay management, or bot-style streaming.
- Prefer `--json` or `--jsonl` for automation and agent workflows.
- Prefer `nostr login --new` for fresh test identities.
- Prefer interactive `nostr login` over `nostr login --nsec ...` for real secrets, because putting an `nsec` in shell arguments leaks into shell history and process lists.
- Prefer an explicit `--account` for automation and agent-initiated writes so they do not depend on the active account.
- Prefer `nostr reply` over hand-assembling reply tags with `nostr event new` when replying to an existing note.
- Prefer `nostr post -f ...` or `nostr post --title ... --slug ...` for long-form content instead of building kind `30023` manually.

## Safety rules

- Treat `post`, `reply`, `dm`, `follow`, `unfollow`, `profile update`, `alias`, `relays add`, `relays rm`, and `update` as external or state-changing actions.
- Confirm the final text and target before any post, reply, or DM.
- Confirm the target account before follow, unfollow, alias changes, or profile edits.
- Confirm relay mutations before adding or removing relays.
- Resolve the intended sender from `nostr accounts --json`, then pass `--account` explicitly for agent-initiated writes and automation.
- Use `--dry-run` before publishing when available, then ask for confirmation before the real send.
- When a command has no `--dry-run`, use `--json` or `--jsonl` for inspection and ask for confirmation before the real send.
- Do not expose `nsec` values in chat output, command output, or saved logs.

## Gotchas

- The command name is `nostr`, not `nostr-cli`.
- `nostr accounts --json` exits non-zero with `No accounts found. Run 'nostr login' to create one.` when no account exists yet.
- `nostr relays --json` also fails until an account is set up.
- `nostr switch --json` is a safe way to list local accounts before choosing an explicit `--account` for a write.
- `nostr dm` sends NIP-17 gift-wrapped DMs by default; use `--nip04` only when the other side requires the legacy mode.
- `nostr events --kinds 4 ...` auto-decrypts DMs when the private key is available; use `--no-decrypt` or `--raw` when you need wire-format inspection.
- `nostr dm --watch` and `nostr events --watch` keep running and stream data; remember to bound them with `--since` or stop them explicitly.
- `--raw` returns wire-format events, while `--json` and `--jsonl` include enriched metadata.
- All state lives under `~/.nostr/`; each account has its own isolated relays, aliases, cache, and local backups.
