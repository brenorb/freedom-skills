# Protection and final verification

## Sign and encrypt

For an authorized NIP-46 signer, use `--use-signer` on both creation and
updates. Connect only when needed, and save the response once:

```sh
npx --yes nowhere-cli signer connect --bunker "$BUNKER_URI" --json > connect.json
```

Set the input's `pubkey` to `pubkeyHex` from `connect.json` before creation.
**`--use-signer` does not fill a missing author key.** A CLI response can contain
a purported signed URL that `verify` still identifies as unsigned when the
embedded author is absent. Include the user's requested name/body in
`message.json` and the narrow requested changes in `patch.json`, then:

```sh
npx --yes nowhere-cli create message --input message.json --use-signer --json > original.json
SITE_URL=$(node -p 'JSON.parse(require("fs").readFileSync("original.json", "utf8")).url')
npx --yes nowhere-cli update "$SITE_URL" --patch patch.json --use-signer --json > final.json
SITE_URL=$(node -p 'JSON.parse(require("fs").readFileSync("final.json", "utf8")).url')
npx --yes nowhere-cli verify "$SITE_URL" --json > verify.json
```

Require `verify.json` to contain `signed: true` and `signaturePubkeyHex` matching
the connected public key. If either check fails, repair the author/signing state
before declaring success. Open and deliver **the URL read from `final.json`**;
do not copy an earlier tool response or rerun signing to capture output. Repeated
signatures can produce different URL fragments for identical content. Disconnect
only a test signer created for this task when requested, then check its status:

```sh
npx --yes nowhere-cli signer disconnect --json
npx --yes nowhere-cli signer status --json > disconnected.json
```

For local keys, `sign` takes `--secret`; `create` and `update` take
`--sign-secret`. The key must match the embedded author public key. Do not echo
private keys or include them in delivered reports. Static sites needing signing
should include the intended author `pubkey` at creation.

When an authorized secret's public encodings need checking, derive them with
`npx --yes nowhere-cli pubkey --secret "$AUTHOR_SECRET" --json`. Its `pubkeyHex`,
`npub`, and Nowhere public-key encoding represent the same key. Nostr public keys
contain 32 bytes (64 hex characters); keep all bytes, including the first one.
Use the CLI's conversions and signature verification for these checks.

```sh
npx --yes nowhere-cli create message --input message.json --sign-secret "$AUTHOR_SECRET" --json
npx --yes nowhere-cli update "$SITE_URL" --patch patch.json --sign-secret "$AUTHOR_SECRET" --json
npx --yes nowhere-cli encrypt "$SITE_URL" --password "$LINK_PASSWORD" --json
npx --yes nowhere-cli decrypt "$SITE_URL" --password "$LINK_PASSWORD" --json
npx --yes nowhere-cli verify "$SITE_URL" --password "$LINK_PASSWORD" --json
```

Sign the final content before encryption. For protected updates, `--password`
decrypts the input; `--encrypt-password` encrypts the output. **Decrypting an input
does not re-encrypt the result**, and editing signed content requires a fresh
signature. Supply the appropriate output options to preserve required protections.
If credentials are unavailable, report the unfinished protection step rather than
presenting a downgraded link as complete.

Create/update JSON `url` is the final output after requested signing/encryption.
Standalone sign returns `signedUrl`; encrypt returns `encryptedUrl`; decrypt
returns a plaintext `url`. `inspect --password` also exposes a decrypted URL.
Never deliver those plaintext variants when the requested artifact is encrypted.

## Completion checks

1. Inspect the final URL (with `--password` only when needed). Confirm `site.siteType`,
   `site.name`, intended `pubkeyHex`, and verification phrases. `forum` decodes as
   `discussion`. `inspect` provides a summary, not the complete content.
2. Open the exact final URL in a fresh browser view. Check requested body text,
   images/SVG, dates, destinations, or other app-specific details. For updates,
   check that fields outside the requested patch still appear correctly.
3. If signing is required, `verify` must return `signed: true` and the expected
   `signaturePubkeyHex`. Exit code zero also occurs for unsigned pages; it is not
   enough. Check the password flow when encryption is required.
4. For relay operations, save returned IDs/receipts and confirm the operation
   through the matching read path using the same URL, relays, and salt. Follow
   each app's limitations for counts, decryption, moderation, and ephemeral chat.
5. Deliver the final link, a concise account of what was verified, and any
   unresolved limitation. If no browser is available, report CLI verification
   and explicitly state that visual rendering remains unchecked. Do not claim
   delivery, payment, or retention from encoding or relay acknowledgement alone.

Keep old URLs when updating: static copies do not change automatically. A site
phrase identifies content; an author phrase identifies a key. Neither is a
substitute for a valid signature when authorship must be established.
