# signal-cli onboarding

Read this file only when `signal-cli` is missing, `signal-cli -o json listAccounts` returns no linked account, or the user explicitly asks for setup help.

## Verify the local state

```bash
command -v signal-cli
signal-cli --version
signal-cli -o json listAccounts
```

## Install

### macOS

```bash
brew install signal-cli
signal-cli --version
```

### Linux

Use the latest generic JVM release:

```bash
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} https://github.com/AsamK/signal-cli/releases/latest | sed -e 's/^.*\/v//')
curl -L -O https://github.com/AsamK/signal-cli/releases/download/v"${VERSION}"/signal-cli-"${VERSION}".tar.gz
sudo tar xf signal-cli-"${VERSION}".tar.gz -C /opt
sudo ln -sf /opt/signal-cli-"${VERSION}"/bin/signal-cli /usr/local/bin/
signal-cli --version
```

### Windows

Download the latest generic release from:

`https://github.com/AsamK/signal-cli/releases/latest`

Install Java if needed, extract to a stable location such as `C:\Tools\signal-cli`, and add the extracted `bin` directory to `PATH`.

## Link as a secondary device

Prefer linking to the user's existing Signal account instead of registering a separate phone number.

```bash
signal-cli link -n "signal-cli"
```

Then ask the user to open Signal on their phone and complete:

1. `Settings`
2. `Linked Devices`
3. `Link New Device`
4. Scan the QR code or open the `sgnl://linkdevice?...` link
5. Approve the new device

## Select the linked account

```bash
signal-cli --version
signal-cli -o json listAccounts
```

For signal-cli 0.14.9+, account JSON contains `number` (which may be null) and `aci`. Identify the account the user intends to use, then reuse that exact E.164 number or ACI in every `--account` argument. Do not choose the first row or infer that a null number means setup failed. For example, a numberless account can look like:

```json
[
  {"number": null, "aci": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"}
]
```

The UUID above is a fixture, not an account to use. Substitute the intended account's actual ACI:

```bash
signal-cli --account "ACCOUNT_ACI_FROM_LIST" receive
python3 scripts/find_contact.py --account "ACCOUNT_ACI_FROM_LIST" --query "Alice"
```

ACI account selection for linked numberless accounts requires 0.14.9+. Older help text may still describe `--account` as phone-number-only; the released manual and account JSON contract are authoritative. If an older client cannot use the intended ACI, report the version limitation; do not switch to another account or fabricate a phone number. Update the client only within the user's requested setup scope.

`listContacts` uses `uuid` for a contact's ACI and can return `number: null`. The helper retains that UUID and includes such rows in ambiguity checks. Existing E.164 contact and account arguments remain valid. PNI-prefixed identifiers and username-prefixed raw CLI arguments are separate forms; the send helper's explicit identifier support is limited to E.164 numbers and full ACI UUIDs.

A note-to-self test is optional and sends a real message. Run it only when requested or authorized:

```bash
signal-cli --account "ACCOUNT_FROM_LIST" send --note-to-self -m "Test from signal-cli"
```

If `listAccounts` is still empty after linking, inspect:

- `$XDG_DATA_HOME/signal-cli/data/`
- `$HOME/.local/share/signal-cli/data/`

Keep the final account, recipient and text explicit before any authorized send.


## Compatibility evidence

Account selection and JSON fields were checked against the released [signal-cli 0.14.9](https://github.com/AsamK/signal-cli/releases/tag/v0.14.9), commit [`3997429779095ff3a2d64c877126e84fce9852aa`](https://github.com/AsamK/signal-cli/tree/3997429779095ff3a2d64c877126e84fce9852aa). The [manual](https://github.com/AsamK/signal-cli/blob/3997429779095ff3a2d64c877126e84fce9852aa/man/signal-cli.1.adoc) permits ACI account selectors and UUID recipients; `ListAccountsCommand` emits `number`/`aci`, while `ListContactsCommand` emits nullable `number` and ACI `uuid`. Tests use synthetic account/contact JSON and mocked commands. They do not inspect a user's account store, link devices, receive messages, start a daemon or send messages.
