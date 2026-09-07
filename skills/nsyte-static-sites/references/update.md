# Update an existing nsite

Publish the new build with the **same publisher and site identifier**:

```bash
nsyte deploy ./dist --name <existing-site-name>
```

For a root site, preserve the root configuration instead of adding a name. A named
site is addressed by publisher plus `d` tag; a newer signed manifest updates its
paths while retaining its URL. Do not generate another publisher or run `init`
again to update an existing site. If the signer is unavailable, recover access
before publishing; a new key creates a different site.

1. Read the existing project's public deployment details and config to identify
   the publisher, name, relay/server destinations, and URL. Keep signing secrets
   out of build files, command arguments, logs, and commits.
2. Edit the existing app and rebuild its complete static output. Preserve the
   original build for comparison or rollback. Use the framework's hashed asset
   filenames, or rename changed plain JS/CSS files and update their HTML references,
   so cached assets cannot leave the new page running old code. Run the bundled port validator
   automatically on the new build, choosing flags based on the updated features.
3. Preview with `nsyte deploy ./dist --name <existing-site-name> --dry-run`.
   Verify the paths include the new code and required assets. Publish with the
   same signer, name, and selected destinations. Do not delete the live site first.
4. Reopen the **same URL**, reload to avoid stale browser assets, and verify a
   specific visible change. Compare retrieved changed files with the build.
   If the gateway still serves the old manifest, check the accepted event and
   gateway cache/relay discovery; do not claim the update is live merely because
   an upload succeeded.

## Adding a small Nostr or Blossom interaction

Choose one operation that exercises a real service, such as reading a few public
Nostr notes or fetching a public Blossom blob. A static frontend can do either;
no private signing key belongs in the browser bundle for these read-only tasks.

- Use configurable runtime endpoints and follow the skill's port rules for the
  intended environment. Establish where the target browser's relay on `4870` or
  Blossom service on `24243` actually lives. A literal placeholder is not a working
  connection. Do not insert unused endpoints just to satisfy the validator.
- For Nostr, send a bounded subscription, show returned public events, close the
  subscription when complete, and handle timeout/disconnect/no-results states.
  Render event text as text, not HTML supplied by the relay.
- For Blossom, fetch a known public blob by hash, verify its SHA-256, and show a
  useful result. Handle CORS, timeouts, and missing blobs visibly.
- Test a successful real read in the intended browser and a failed connection.
  An attractive loading screen, port-validation pass, or mocked response alone
  does not establish that the interaction works. Report any unavailable runtime
  service separately from whether publication succeeded.

If a regression needs rollback, rebuild the preserved previous source and publish
it again with the same publisher/name, producing a newer manifest. Retain the
previous content until the update is verified; removing remote blobs could break
cached or older site versions.
