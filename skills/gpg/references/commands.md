# gpg command patterns

Read this file only when the user needs raw `gpg` patterns beyond the default workflow in `SKILL.md`.

Use the trust-changing, keyserver, signing, and deletion examples here only after the user confirmed the intended identity and outcome.

## Inspect local setup

```bash
gpg --version
gpgconf --list-dirs
gpg --list-keys --keyid-format long
gpg --list-secret-keys --keyid-format long
```

## Inspect keys with machine-readable output

```bash
gpg --list-keys --with-colons --fingerprint "alice@example.com"
gpg --list-secret-keys --with-colons --fingerprint "alice@example.com"
```

## Symmetric file encryption

```bash
gpg --symmetric --cipher-algo AES256 --output secret.txt.gpg secret.txt
gpg --decrypt --output secret.txt secret.txt.gpg
```

Prefer this when one person needs to lock and later unlock a local file with a passphrase.

## Import and export public keys

```bash
gpg --import alice.pub.asc
gpg --armor --export "Alice Example <alice@example.com>" > alice.pub.asc
gpg --dearmor alice.pub.asc
```

## Encrypt and decrypt with recipient keys

```bash
gpg --batch --yes --trust-model always --armor --output secret.txt.asc --encrypt --recipient "Alice Example <alice@example.com>" secret.txt
gpg --batch --yes --output secret.txt --decrypt secret.txt.asc
gpg --batch --yes --trust-model always --output archive.tar.gz.gpg --encrypt --recipient "Alice Example <alice@example.com>" archive.tar.gz
```

Use `--trust-model always` only after the recipient fingerprint is verified.

## Sign and verify

```bash
gpg --armor --output message.txt.asc --clear-sign message.txt
gpg --armor --output release.tar.gz.sig --detach-sign release.tar.gz
gpg --armor --output note.asc --sign note.txt
gpg --verify message.txt.asc
gpg --verify release.tar.gz.sig release.tar.gz
```

## Sign and encrypt in one step

```bash
gpg --batch --yes --trust-model always --armor --output note.asc --encrypt --sign --local-user "Alice Example <alice@example.com>" --recipient "Bob Example <bob@example.com>" note.txt
```

## Discover keys from the network

```bash
gpg --locate-keys alice@example.com
gpg --search-keys alice@example.com
gpg --recv-keys BFA682C9686198C2BC8A84CBCC7BFE5EBB0DBD0B
```

Always verify the imported fingerprint before using a network-fetched key.

## Publish keys to a public keyserver

```bash
gpg --send-keys BFA682C9686198C2BC8A84CBCC7BFE5EBB0DBD0B
```

Treat this as public and hard to undo.

## Sensitive key material commands

```bash
gpg --armor --export-secret-keys "Alice Example <alice@example.com>" > alice.secret.asc
gpg --armor --export-secret-subkeys "Alice Example <alice@example.com>" > alice.subkeys.asc
gpg --output revoke-alice.asc --armor --generate-revocation "Alice Example <alice@example.com>"
```

Do not use these without explicit user intent.

## Trust and signatures on keys

```bash
gpg --quick-sign-key BFA682C9686198C2BC8A84CBCC7BFE5EBB0DBD0B
gpg --quick-lsign-key BFA682C9686198C2BC8A84CBCC7BFE5EBB0DBD0B
gpg --check-signatures "alice@example.com"
```

Only sign a key after out-of-band fingerprint verification.

## Deletion

```bash
gpg --delete-keys "alice@example.com"
gpg --delete-secret-keys "alice@example.com"
```

Back up the right material first and confirm whether the user means public keys, secret keys, or both.

## Low-level inspection

```bash
gpg --list-packets message.txt.asc
gpg --print-md sha256 release.tar.gz
```
