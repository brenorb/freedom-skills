---
name: signal-cli
description: Receive Signal messages, read or search previously captured Signal messages, send messages and attachments, or inspect accounts, contacts, and groups with signal-cli. Also use for linking an account or troubleshooting Signal CLI access.
---

# signal-cli

Use the local `signal-cli` binary for Signal messaging. Choose the workflow that matches the request; receiving new events and searching an existing capture are different operations.

## Read or search messages

For incoming messages or local history search, read
[references/message-history.md](references/message-history.md). Start with an
existing capture for history queries; use JSON `receive` for new pending messages.
Do not sync first and discard the output needed for the user's inspection.
`receive` is not a query of the phone's historical inbox.

## Sending workflow

1. When the account is known, sync it once before contact/group lookup or sending:

```bash
signal-cli -u "+15551234567" receive
```

2. Use the bundled scripts for recipient resolution and sending:

```bash
python3 scripts/find_contact.py --account "+15551234567" --query "Alice"
python3 scripts/send_message.py --account "+15551234567" --to "Alice" --text "hello"
python3 scripts/send_message.py --account "+15551234567" --to "Alice" --text "see attachment" --attachment "/path/to/file"
```

3. If the account is uncertain, inspect `signal-cli listAccounts`. If the binary
   is missing or no account is linked, read `references/onboarding.md` before
   retrying the action. Do not require setup checks for an already working account.
4. For other raw CLI patterns, read `references/commands.md`.

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
