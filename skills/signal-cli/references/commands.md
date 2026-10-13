# signal-cli command patterns

Read this file only when the user needs raw `signal-cli` command patterns beyond the default workflow in `SKILL.md`.

## Discover accounts

```bash
signal-cli listAccounts
```

## Sync an account

```bash
signal-cli -u "+15551234567" receive
```

## Receive incoming messages as JSON

```bash
signal-cli -o json -a "+15551234567" receive --timeout 5 --ignore-attachments
```

This emits newline-delimited events for pending messages, not a historical inbox.
Read [message-history.md](message-history.md) to retain captures and search them
with `jq`. Capture first if the user needs the message contents: an earlier plain
`receive` used only for syncing does not provide a replayable history.

## List contacts as JSON

```bash
signal-cli -o json -u "+15551234567" listContacts
```

## List groups as JSON

```bash
signal-cli -o json -u "+15551234567" listGroups
```

## Send to note to self

```bash
signal-cli -u "+15551234567" send --note-to-self -m "Test from signal-cli"
```

## Send directly to a phone number

```bash
signal-cli -u "+15551234567" send "+15557654321" -m "hello"
```

## Send an attachment

```bash
signal-cli -u "+15551234567" send "+15557654321" -m "see attachment" -a "/path/to/file"
```

## Send to a group

List groups first, then send with the group id:

```bash
signal-cli -o json -u "+15551234567" listGroups
signal-cli -u "+15551234567" send -g "GROUP_ID" -m "hello group"
```
