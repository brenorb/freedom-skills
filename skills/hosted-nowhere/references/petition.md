# Petition

```sh
npx --yes nowhere-cli create petition --input petition.json --json > final.json
SITE_URL=$(node -p 'JSON.parse(require("fs").readFileSync("final.json", "utf8")).url')
```

Use [petition.json](../examples/petition.json), replacing `pubkey` with the
intended owner's key. Fields include `name`, `description`, `image`, and `tags`.
Signature data is encrypted to that owner; a public key without its matching
private key cannot recover submissions. Use the user's key for real petitions.

Browser: `https://hostednowhere.com/create/petition`. Check requested signer fields,
country restrictions, the owner phrase, and final content before sharing.

## Sign, count, and review

Use the `SITE_URL` extracted from the saved creation response above for **every**
sign/count/review/export and the final browser check. Never retype or reconstruct
its fragment: even a valid-looking truncated URL may decode to different content
and send the signature to another petition. Inspect that exact URL before the
first publish. If a submission went to the wrong URL, stop and report it; do not
silently submit a second signature as a repair.

In these examples, `RELAY` is the supplied relay URL. Keep the explicit override
on signing, counting, owner review, and CSV export. If the user chose no relay,
the flag may be omitted to use the CLI defaults.

```sh
npx --yes nowhere-cli petition sign "$SITE_URL" --input signature-input.json --secret "$SIGNER_SECRET" --json --relay "$RELAY" > signature.json
npx --yes nowhere-cli petition count "$SITE_URL" --json --relay "$RELAY" > count.json
npx --yes nowhere-cli petition signatures "$SITE_URL" --secret "$OWNER_SECRET" --json --relay "$RELAY" > owner.json
npx --yes nowhere-cli petition signatures "$SITE_URL" --secret "$OWNER_SECRET" --csv --relay "$RELAY" > owner.csv
```

`signature-input.json` contains signer data, for example
`{"name":"Alex","email":"alex@example.com","country":"BR"}`.
`signature.json` above is the **captured command response**, including `event.id`;
it is not the signer input. Use the user's requested output names and keep input
filenames distinct. Read the saved response after publishing; never publish again
just to obtain a copy of it. Prepare only the
requested fields, respecting the actual petition. Uppercase tags such as `N` and
`E` make name/email required; tag `c` contains dot-separated allowed countries.
Other required fields must be satisfied too. Anonymous signing omits `--secret`;
choose it only when anonymous submission is intended. Publishing is a relay write.

Use an already configured remote signer with `--use-signer` instead of `--secret`
where available. Counts are not a substitute for successful owner decryption.
Inspect JSON entries' `payload` and `decryptError`, plus rejected proof-of-work
counts, before export. CSV omits failed decryptions: report omissions and retain
JSON when the result will feed another script. Do not combine `--csv` and `--json`.

## Updates and retries

Petition relay lookup is derived from the fragment. Treat an edited URL as a new
petition namespace: preserve the original link to retrieve its signatures. Do not
promise existing signatures migrate automatically. On a publish timeout, keep
any returned event ID and query the same petition/relays before retrying. A public
count alone cannot prove that a particular submission arrived.

## CLI and browser observations

`--relay` selects the relay for that CLI operation; it does not edit the link or
reconfigure the browser page. A CLI count and a browser count can therefore
observe different relay state. Keep the accepted event ID, count, and owner
JSON/CSV from the requested relay, and report the browser observation separately.
Do not submit another signature, edit the petition, or switch relays merely to
make the displayed count match. A correct page title and verification phrase
confirm page content, not synchronization with the CLI's selected relay.

If the user specifically requires a matching live browser count and it is not
confirmed, report that step as unverified. Do not claim the browser displays a
signature solely because the CLI retrieved it, or treat an empty browser count
as proof that the authorized submission failed.
