# signal-cli command patterns

Read this file only when the user needs raw `signal-cli` command patterns beyond the default workflow in `SKILL.md`.

## Discover accounts

```bash
signal-cli -o json listAccounts
```

Use the explicitly intended row's `number` or `aci`; `number` can be null. ACI sender selection for linked numberless accounts requires signal-cli 0.14.9+. The examples below use an E.164 sender, but the same global `--account` argument accepts its ACI. Never substitute another account when a client rejects the intended selector.

## Sync an account

```bash
signal-cli --account "+15551234567" receive
```

## List contacts as JSON

```bash
signal-cli -o json --account "+15551234567" listContacts
```

## List groups as JSON

```bash
signal-cli -o json --account "+15551234567" listGroups
```

## Send to note to self

```bash
signal-cli --account "+15551234567" send --note-to-self -m "Test from signal-cli"
```

## Send directly to a phone number

```bash
signal-cli --account "+15551234567" send "+15557654321" -m "hello"
```

## Resolve a numberless contact or use an explicit ACI

`listContacts` returns an ACI in `uuid`, even when `number` is null. Inspect the intended contact before sending. The helper resolves an unambiguous name to that saved UUID; an explicitly supplied recipient UUID must be complete, including dashes.

```bash
python3 scripts/find_contact.py --account "ACCOUNT_FROM_LIST" --query "Alice"
python3 scripts/send_message.py --account "ACCOUNT_FROM_LIST" --to "RECIPIENT_ACI_FROM_CONTACTS" --text "hello"
```

The `ACCOUNT_FROM_LIST` and `RECIPIENT_ACI_FROM_CONTACTS` strings are placeholders for identifiers already selected for the task. An ambiguous lookup returns candidates (including UUIDs) and exits without sending. A contact lacking both a usable phone number and ACI also stops; a weaker name match is not substituted.

## Send an attachment

```bash
signal-cli --account "+15551234567" send "+15557654321" -m "see attachment" -a "/path/to/file"
```

## Send to a group

List groups first, then send with the group id:

```bash
signal-cli -o json --account "+15551234567" listGroups
signal-cli --account "+15551234567" send -g "GROUP_ID" -m "hello group"
```
