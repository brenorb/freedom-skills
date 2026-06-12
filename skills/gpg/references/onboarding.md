# gpg onboarding

Read this file only when `gpg` is missing, the user needs a keypair, the user needs to import keys for the first time, or signing and decrypting are blocked by pinentry or agent setup.

## Verify local state

```bash
command -v gpg
gpg --version
gpg --list-keys --keyid-format long
gpg --list-secret-keys --keyid-format long
gpgconf --list-dirs
```

If `--list-secret-keys` is empty, the machine has no local OpenPGP identity yet.

## Install

### macOS

```bash
brew install gnupg pinentry-mac
gpg --version
```

If pinentry prompts do not appear on macOS:

```bash
mkdir -p ~/.gnupg
chmod 700 ~/.gnupg
printf 'pinentry-program %s\n' "$(command -v pinentry-mac)" >> ~/.gnupg/gpg-agent.conf
gpgconf --kill gpg-agent
```

### Debian or Ubuntu

```bash
sudo apt update
sudo apt install -y gnupg pinentry-curses
gpg --version
```

### Fedora

```bash
sudo dnf install -y gnupg2 pinentry
gpg --version
```

### Arch

```bash
sudo pacman -S --needed gnupg pinentry
gpg --version
```

### Windows

Install Gpg4win from:

`https://gpg4win.org`

Then open PowerShell and verify:

```powershell
gpg --version
```

## Create a new keypair

Prefer a user-run terminal step for real identities so the user enters the passphrase directly in pinentry:

```bash
gpg --full-generate-key
```

For a quick modern default on a local test identity:

```bash
gpg --quick-generate-key "Alice Example <alice@example.com>" future-default default 1y
```

After creation:

```bash
gpg --list-secret-keys --keyid-format long
gpg --list-keys --with-colons --fingerprint "alice@example.com"
```

## Export the public key

```bash
gpg --armor --export "Alice Example <alice@example.com>" > alice.pub.asc
```

Share only the public key and the fingerprint, not the secret key.

## Import someone else's public key

```bash
gpg --import alice.pub.asc
gpg --list-keys --with-colons --fingerprint "alice@example.com"
```

Verify the fingerprint with the owner over a trusted channel before using the key for encryption.

## First self-test

After a keypair exists locally, verify encrypt and decrypt to self:

```bash
printf 'test from gpg\n' > gpg-test.txt
gpg --batch --yes --armor --output gpg-test.txt.asc --encrypt --recipient "Alice Example <alice@example.com>" gpg-test.txt
gpg --batch --yes --output gpg-test.out.txt --decrypt gpg-test.txt.asc
cat gpg-test.out.txt
```

Then verify signing:

```bash
gpg --batch --yes --armor --output gpg-test.txt.sig --detach-sign gpg-test.txt
gpg --verify gpg-test.txt.sig gpg-test.txt
```

## Generate a revocation certificate

Do this soon after key creation and store the result offline:

```bash
gpg --output revoke-alice.asc --armor --generate-revocation "Alice Example <alice@example.com>"
```

Treat the revocation certificate as sensitive because anyone with it can revoke the key publicly.

## Local state

Key material, trust data, sockets, and agent state live under `~/.gnupg/`.

Treat that directory as sensitive, especially:

- `private-keys-v1.d/`
- `pubring.kbx`
- `trustdb.gpg`
- `openpgp-revocs.d/`
- `gpg-agent.conf`
