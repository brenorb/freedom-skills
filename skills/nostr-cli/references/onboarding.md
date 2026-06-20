# nostr-cli onboarding

Read this file only when `nostr` is missing, `nostr accounts --json` reports no accounts, or the user explicitly asks for setup help.

## Verify local state

```bash
command -v nostr
nostr version --json
nostr accounts --json
```

If the last command says `No accounts found`, that is a normal first-run state.

## Install

Source of truth:

- Repo: `https://github.com/xdamman/nostr-cli`
- Website: `https://nostrcli.sh`

### macOS / Linux shell installer

```bash
curl -sf https://nostrcli.sh/install.sh | sh
nostr version --json
```

### macOS / Linux via Homebrew

```bash
brew install xdamman/tap/nostr
nostr version --json
```

### Debian / Ubuntu

Download the latest `.deb` from the repo releases, then:

```bash
sudo dpkg -i nostr_*.deb
nostr version --json
```

### Fedora / RHEL / openSUSE

Download the latest `.rpm` from the repo releases, then:

```bash
sudo rpm -i nostr_*.rpm
nostr version --json
```

### From source

```bash
git clone https://github.com/xdamman/nostr-cli.git
cd nostr-cli
make install
nostr version --json
```

## Create or import an account

Ask the user if they prefer a fresh test account or want to use an existing identity.

### Generate a new keypair

```bash
nostr login --new
```

### Import an existing key

Prefer this as a user-run terminal step so the agent will not leak the `nsec`. If the user is non technical, help him understand what terminal step he needs to run in concise terms.

```bash
nostr login
```

Only use `nostr login --nsec nsec1...` when the user explicitly asks the local agent to handle the secret in a local-enough setup and explicitly accepts shell-history and process-list exposure.

## First relay setup

After account creation or import:

```bash
nostr relays add wss://relay.damus.io --account my-account
nostr relays add wss://nos.lol --account my-account
nostr relays --account my-account --json
```

## First safe write test

Prefer a dry run before a real post:

```bash
nostr post "Test from nostr-cli" --account my-account --dry-run --json
```

Then, only if the user wants to actually publish:

```bash
nostr post "Test from nostr-cli" --account my-account --json
```

## Local state

Account data lives under `~/.nostr/accounts/<npub>/`, including:

- `nsec`
- `profile.json`
- `relays.json`
- `aliases.json`
- `events.jsonl`
- `directmessages/`
- `cache/`

Treat that directory as sensitive because it contains private keys and local message history.
