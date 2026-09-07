# Validation — 2026-09-07

Tested with installed nsyte 0.27.2 on macOS, using a temporary project,
disposable signing key, `dist/index.html`, and `dist/style.css`.

- `deploy --help`, `download --help`, and `serve --help` confirm the documented flags.
- `deploy ./dist --dry-run` with explicit local relay/server destinations and
  `--no-config` succeeded. The generated kind-15128 manifest contains exactly
  `/index.html` and `/style.css`; both hashes matched SHA-256 of the input files.
- An absolute deployment path incorrectly found zero files and returned success.
  The workflow therefore uses a relative path and checks manifest contents.
- Omitting Blossom servers failed with `Servers configuration is missing or empty`.

No real publication was completed. The earlier test tried unavailable local
services on ports 4870 and 24243 as publication destinations. The supplied
instructions describe those ports as app connections; their absence does not
block deployment to other configured destinations. A dry run does not establish upload, relay acceptance,
independent retrieval, or public gateway access. Those remain required before
declaring this workflow verified end to end.

## Complete the remaining acceptance check

Use a disposable publisher and destinations selected for the test. Create a small
static build containing HTML and one stylesheet. Preview its manifest, publish,
then run the skill's download command from a separate client into a new directory.
Compare both downloaded files with the originals, and open the actual gateway
URL to confirm the stylesheet loads. Record CLI version, public destinations,
manifest paths/hashes, and the retrieval result. Never record signing credentials.
