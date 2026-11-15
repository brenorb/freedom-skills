# Art

```sh
npx --yes nowhere-cli create art --input art.json --json
```

Use [art.json](../examples/art.json). Put actual SVG markup in `svg`, with
optional `name`, `pubkey`, and `tags`. JSON-escape quotes and line breaks normally;
do not pass a filesystem path as the SVG content.

Browser: `https://hostednowhere.com/create/art`. Provide SVG content, then check
the rendered geometry, colors, and viewBox before copying the final Share Link.
The CLI can encode data without proving the artwork renders correctly.

Art is a static page, with no relay-backed publishing flow. SVG content is needed
for a meaningful result even if a codec accepts a title-only payload.

Share the artwork as a Markdown link with a short artwork-name label. Put the
complete final URL from the saved CLI JSON in the link target, keeping every
character of its fragment. The fragment is required to load the artwork; do not
shorten it or replace parts with placeholders.
