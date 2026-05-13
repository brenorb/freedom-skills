---
name: signal-cli
description: Use this skill when the user wants to send a Signal message or attachment to a person or group, even if they ask in terms of messaging someone rather than using signal-cli explicitly. It also applies when the user needs to set up or troubleshoot Signal CLI access, link Signal on a computer, or inspect Signal accounts, contacts, or groups.
---

# signal-cli

Use the local `signal-cli` binary to send Signal messages and attachments. Account inspection, syncing, and recipient resolution support that primary workflow.

## Default workflow

1. Check whether `signal-cli` is installed and linked:

```bash
command -v signal-cli
signal-cli listAccounts
```

2. If the binary is missing or `listAccounts` is empty, read `references/onboarding.md` and complete setup before trying to send anything.
3. Before listing contacts, listing groups, or sending, sync the account once:

```bash
signal-cli -u "+15551234567" receive
```

4. Use the bundled scripts for recipient resolution and sending:

```bash
python3 scripts/find_contact.py --account "+15551234567" --query "Alice"
python3 scripts/send_message.py --account "+15551234567" --to "Alice" --text "hello"
python3 scripts/send_message.py --account "+15551234567" --to "Alice" --text "see attachment" --attachment "/path/to/file"
```

5. If the user asks for raw CLI usage patterns beyond the defaults here, read `references/commands.md`.

## Defaults

- Prefer linking `signal-cli` as a secondary device to the user's existing Signal account.
- Prefer the bundled scripts over handwritten `signal-cli` command assembly for contact lookup and person-to-person sends.
- Use E.164 phone numbers (`+15551234567`) for account and direct recipient arguments.
- After first-time setup, send `--note-to-self` before messaging another person or group.

## Safety rules

- Confirm the final recipient and final message text before any send.
- If recipient lookup returns multiple candidates, stop and ask the user which one to use.
- If the message contains sensitive information, ask explicitly before sending it via Signal.
- When sending to a group, confirm the intended group after listing candidate groups or group ids.

## Gotchas

- `signal-cli` can look healthy while no account is linked; `listAccounts` is the real check.
- Contacts, groups, and profile state can be stale until `receive` runs.
- Group sends may report warnings for stale or unregistered members while still delivering successfully. Treat that as sent only when the command exits successfully.
- `listContacts` and `listGroups` are easiest to automate with `-o json`.
