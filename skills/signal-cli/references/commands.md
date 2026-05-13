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
