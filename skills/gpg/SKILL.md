---
name: gpg
description: "Use this skill when Codex needs to work with the local `gpg` command from GnuPG for OpenPGP workflows: inspect keyrings, import or export keys, encrypt or decrypt files, sign or verify content, or troubleshoot trust and pinentry issues."
---

# gpg

Use the local `gpg` binary for OpenPGP encryption, decryption, signatures, and key inspection.

## Default workflow

1. Start with the command that directly matches the user's goal:

```bash
gpg --armor --export "Alice Example <alice@example.com>" > alice.pub.asc
gpg --batch --yes --trust-model always --armor --output secret.txt.asc --encrypt --recipient "Alice Example <alice@example.com>" secret.txt
gpg --batch --yes --output secret.txt --decrypt secret.txt.asc
gpg --batch --yes --armor --output release.tar.gz.sig --detach-sign release.tar.gz
gpg --verify release.tar.gz.sig release.tar.gz
```

2. Before importing a new key, trusting a key, or encrypting to a key from the network, inspect the exact fingerprint:

```bash
gpg --list-keys --with-colons --fingerprint "alice@example.com"
```

3. If the action fails because `gpg` is missing, the keyring is missing the right key, the user needs a new keypair, or pinentry is blocking sign or decrypt, read `references/onboarding.md`.
4. If you need a broader view of the local keyring before choosing a target key, inspect it directly:

```bash
gpg --list-keys --keyid-format long
gpg --list-secret-keys --keyid-format long
```

5. If the user asks for raw command patterns beyond the defaults here, read `references/commands.md`.

## Defaults

- Prefer ASCII armor with `--armor` for files that may be pasted, shared in chat, or inspected by a human.
- Prefer `--with-colons --fingerprint` for machine-readable key inspection.
- Prefer `--batch --yes` for agent-initiated noninteractive commands.
- Prefer using the user's existing secret key instead of generating a new keypair unless the user asks for a new identity.
- After the user verifies a recipient fingerprint, prefer per-command `--trust-model always` over changing global trust settings just to make one encryption command succeed.
- Prefer an isolated `GNUPGHOME` for experiments, demos, or tests that should not touch the user's real keyring.

## Safety rules

- Never print, export, back up, transmit, or delete secret keys unless the user explicitly asks.
- Treat passphrases, private keys, revocation certificates, and `~/.gnupg/` contents as sensitive.
- Prefer user-run terminal steps for entering passphrases or importing private keys. If the user explicitly wants the local agent to handle secret material, avoid shell arguments and keep it local.
- Confirm the final recipient fingerprint before encrypting when multiple keys match, the key was fetched from the network, or the identity is ambiguous.
- Confirm before `--send-keys`, `--sign-key`, `--lsign-key`, `--quick-sign-key`, `--quick-lsign-key`, `--delete-keys`, `--delete-secret-keys`, or revocation generation.
- Before deleting keys, export the right backup first and confirm whether the user means public keys, secret keys, or both.

## Gotchas

- Importing a public key does not automatically make it usable for batch encryption. After fingerprint verification, `--trust-model always` is the simplest per-command bypass.
- `gpg` often delegates passphrase prompts to `gpg-agent` and pinentry. If a sign or decrypt command appears hung, the user may need to approve a local GUI or TTY prompt.
- `gpg --decrypt` writes plaintext to stdout unless `--output` is set.
- `gpg` defaults to binary output unless `--armor` is used.
- `gpg --verify` can report a good cryptographic signature even when the signer is not trusted. Trust and signature validity are separate questions.
- Matching by email or name can return multiple keys. Use fingerprints to disambiguate before encrypting or signing anything.
