# signal-cli onboarding

Read this file only when `signal-cli` is missing, `signal-cli listAccounts` returns no linked account, or the user explicitly asks for setup help.

## Verify the local state

```bash
command -v signal-cli
signal-cli version
signal-cli listAccounts
```

## Install

### macOS

```bash
brew install signal-cli
signal-cli version
```

### Linux

Use the latest generic JVM release:

```bash
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} https://github.com/AsamK/signal-cli/releases/latest | sed -e 's/^.*\/v//')
curl -L -O https://github.com/AsamK/signal-cli/releases/download/v"${VERSION}"/signal-cli-"${VERSION}".tar.gz
sudo tar xf signal-cli-"${VERSION}".tar.gz -C /opt
sudo ln -sf /opt/signal-cli-"${VERSION}"/bin/signal-cli /usr/local/bin/
signal-cli version
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

## Verify the linked account

```bash
signal-cli listAccounts
signal-cli -u "+15551234567" receive
signal-cli -u "+15551234567" send --note-to-self -m "Test from signal-cli"
```

If `listAccounts` is still empty after linking, inspect:

- `$XDG_DATA_HOME/signal-cli/data/`
- `$HOME/.local/share/signal-cli/data/`

Do not message another person until the note-to-self test succeeds.
