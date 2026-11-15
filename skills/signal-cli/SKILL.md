---
name: signal-cli
description: Use this skill when the user wants to send a Signal message or attachment to a person or group, even if they ask in terms of messaging someone rather than using signal-cli explicitly. It also applies when the user needs to set up or troubleshoot Signal CLI access, link Signal on a computer, or inspect Signal accounts, contacts, or groups.
---

# signal-cli

Use the local `signal-cli` binary to send Signal messages and attachments. Account inspection, syncing, and recipient resolution support that primary workflow.

## Default workflow

1. With a known linked account, start with the requested action. Use the bundled scripts for person-to-person recipient lookup and sending:

```bash
python3 scripts/find_contact.py --account "+15551234567" --query "Alice"
python3 scripts/send_message.py --account "+15551234567" --to "Alice" --text "hello"
python3 scripts/send_message.py --account "+15551234567" --to "Alice" --text "see attachment" --attachment "/path/to/file"
```

2. `--account` accepts the intended sender's E.164 phone number or ACI identifier. For linked accounts without a phone number, use signal-cli 0.14.9+ and the `aci` returned by `signal-cli -o json listAccounts`. A null `number` does not mean an account is unlinked. When the intended account is unknown, list the accounts and identify it explicitly; never select the first account or invent a phone number.
3. The send helper accepts an explicit E.164 number, a full dashed ACI UUID, or a contact name. For a named contact without a phone number, it uses the saved `uuid` from `listContacts`. UUID fields require an exact full match. If lookup is ambiguous or the best match has no usable identifier, stop and resolve that contact before sending.
4. If setup is missing, the client is too old for the account, or account/contact state is uncertain, read `references/onboarding.md`. Sync stale account state with `receive` when needed, then retry the requested lookup; an automatic note-to-self send is not part of setup.
5. For raw commands, including group sends, read `references/commands.md`.

## Defaults

- Prefer linking `signal-cli` as a secondary device to the user's existing Signal account.
- Prefer the bundled scripts over handwritten `signal-cli` command assembly for contact lookup and person-to-person sends.
- Keep the selected sender explicit across lookup, sync and send commands. E.164 accounts remain supported; ACI sender selection for numberless accounts requires 0.14.9+.
- Direct recipients can be E.164 numbers or full ACI UUIDs. A saved UUID identifies a contact; it does not verify that person’s real-world identity.
- Send a note-to-self only if the user requests or authorizes that test.

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
