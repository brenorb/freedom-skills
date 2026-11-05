# Drop

```sh
npx --yes nowhere-cli create drop --input drop.json --json
```

Use [drop.json](../examples/drop.json). `description` is the required text;
`name` is an optional title. Preserve code, line breaks, and Unicode exactly.
Optional author provenance uses `pubkey` and signing, not a relay upload.

Browser: `https://hostednowhere.com/create/drop`. Body text is required even if
there is a title. Confirm the final URL renders all lines correctly.

A Drop carries text in its URL. It is not a file-transfer inbox or a live message
wall. Keep large binary attachments out of this workflow.
