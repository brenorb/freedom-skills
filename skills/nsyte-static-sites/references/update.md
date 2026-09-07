# Update an existing nsite

```bash
nsyte deploy ./dist --name <existing-site-name>
```

1. Reuse the existing publisher, name, and publication destinations. Do not rerun `init`; recover the existing signer if unavailable. For a root site, preserve its root configuration.
2. Preserve the previous build, edit, and rebuild. Use hashed asset filenames, or rename changed JS/CSS files and update HTML references, to avoid stale browser caches.
3. Run the skill's port validator, inspect `--dry-run`, then deploy with the same name and signer.
4. Open the **same URL**, test the change, and compare retrieved changed files with the build. If old content remains, check gateway cache and manifest discovery. An accepted upload alone does not prove the update is live.

Rollback: republish the previous build with the same publisher/name. Retain old remote blobs so cached versions keep working.

## Add a read-only interaction

Use the runtime endpoints required by the main skill. Neither example needs a private key in the frontend:

- **Nostr:** request a small number of public notes, render event content as text, close the subscription, and handle timeout, disconnect, and empty results.
- **Blossom:** fetch a known public blob, verify its SHA-256, and display the result. Handle CORS, timeout, and missing-blob errors.

Test one successful real read and one failed connection in the intended browser. Report unavailable services separately from publication success; mocks or validator passes alone do not prove the feature works.
