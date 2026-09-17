---
name: gpg
description: "Use this skill when Codex needs to work with the local `gpg` command from GnuPG for file encryption with a passphrase or recipient public key, decryption, signatures, key inspection, or trust and pinentry troubleshooting."
---

# gpg

Use the local `gpg` binary for OpenPGP encryption, decryption, signatures, and key inspection.

## Default workflow

1. For the simple "file plus password" case, prefer symmetric encryption and let `gpg` prompt for the passphrase through pinentry:

```bash
gpg --symmetric --cipher-algo AES256 --output secret.txt.gpg secret.txt
gpg --decrypt --output secret.txt secret.txt.gpg
```

2. For recipient-based encryption, inspect the target key fingerprint first, then encrypt:

```bash
gpg --list-keys --with-colons --fingerprint "Alice Example <alice@example.com>"
gpg --batch --yes --trust-model always --armor --output secret.txt.asc --encrypt --recipient "Alice Example <alice@example.com>" secret.txt
```

3. For signatures, use the command that matches the user's intent:

```bash
gpg --armor --output release.tar.gz.sig --detach-sign release.tar.gz
gpg --verify release.tar.gz.sig release.tar.gz
gpg --armor --output note.txt.asc --clear-sign note.txt
```

4. If the action fails because `gpg` is missing, the machine lacks the right key, the user needs a new keypair, or pinentry is blocking sign or decrypt, read `references/onboarding.md`.
5. If the user asks for raw command patterns beyond the defaults here, read `references/commands.md`.

## Defaults

- Prefer symmetric encryption for one-off local file protection where the user only has a password and no recipient public key.
- Prefer recipient public-key encryption when the file must be shared with another person without sharing a passphrase.
- Prefer ASCII armor with `--armor` for outputs that may be pasted, shared in chat, or inspected by a human.
- Prefer `--with-colons --fingerprint` for exact key inspection before encrypting to a recipient.
- Prefer `--batch --yes` for agent-initiated noninteractive commands that do not require passphrase entry.
- Prefer an isolated `GNUPGHOME` for demos, tests, or experiments that should not touch the user's real keyring.

## Safety rules

- Never print, export, transmit, back up, or delete secret keys unless the user explicitly asks.
- Treat passphrases, private keys, revocation certificates, and `~/.gnupg/` contents as sensitive.
- Prefer user-run terminal steps for entering passphrases, creating keys, importing private keys, or decrypting highly sensitive material.
- Never pass a real passphrase on the command line. Use pinentry or another local prompt path instead.
- Confirm the final recipient fingerprint before encrypting when multiple keys match, the key was fetched from the network, or the identity is ambiguous.
- Confirm before `--send-keys`, `--recv-keys`, `--search-keys`, `--sign-key`, `--lsign-key`, `--quick-sign-key`, `--quick-lsign-key`, `--delete-keys`, `--delete-secret-keys`, or revocation generation.
- Before deleting keys, export the right backup first and confirm whether the user means public keys, secret keys, or both.

## Gotchas

- `gpg --decrypt` writes plaintext to stdout unless `--output` is set.
- Importing a public key does not automatically make it usable for batch encryption. After fingerprint verification, `--trust-model always` is the simplest per-command bypass.
- `gpg` often delegates passphrase prompts to `gpg-agent` and pinentry. If a sign or decrypt command appears hung, the user may need to approve a local GUI or TTY prompt.
- Matching by email or name can return multiple keys. Use fingerprints to disambiguate before encrypting or signing anything.
- `gpg --verify` can report a good cryptographic signature even when the signer is not trusted. Trust and signature validity are separate questions.
- Symmetric encryption protects the file only as well as the passphrase. Weak passphrases are weak security even when `AES256` is selected.
