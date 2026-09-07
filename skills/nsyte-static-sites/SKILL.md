---
name: nsyte-static-sites
description: Publish or update static HTML, CSS, JavaScript, and assets on Nostr using nsyte and Blossom storage. Use for deploying built sites and verifying retrieval with configured public or local services. Server-side runtimes require separate hosting.
metadata:
  version: "0.1.0"
  repository: "https://github.com/sandwichfarm/nsyte"
  homepage: "https://nsyte.run"
---

# nsyte Static Sites

Use nsyte to publish a static site to the Nostr network. An nsite is not a conventional web server: its files are content-addressed blobs, usually stored on Blossom servers, and a signed Nostr manifest maps URL paths to those files. Gateways resolve the site from the publisher's npub.

This skill covers static sites only. Client-side JavaScript is allowed, including browser code that talks to a Nostr relay. Server-side rendering, API routes, server actions, databases, private backends, and processes that must stay running are out of scope. If the requested app needs those capabilities, stop and explain that it must be made static first.

## Default workflow

For a built site in an already configured project:

```bash
nsyte deploy ./dist
```

Run from the project root, replace `./dist` with the actual relative build directory, and reuse the existing signer and destinations. Install or initialize only when needed.

1. If the build is missing or stale, run the project's existing build command. Inspect HTML, CSS, JavaScript, and assets. Exclude secrets, credentials, `.env` files, and private data. Client-side code may call external services; server-side code requires separate hosting.
2. For a first publication or changed destination, preview before uploading:

   ```bash
   nsyte deploy ./dist --dry-run
   ```

   Check the reported file count and manifest paths/hashes against the build. Stop if expected files are absent, even when the command returns success. Deployment scans for secrets by default; do not disable that scan. For a separate check use `nsyte scan ./dist`.
3. Deploy the build using the command above. For a single-page app that needs a fallback, use `nsyte deploy ./dist --fallback index.html` and verify nested routes afterward.
4. Inspect upload and relay results. Record the publisher's public key, destinations, and site name when using `--name`. Report failed uploads or rejected events explicitly.
5. Download into a fresh directory with a separate read operation:

   ```bash
   nsyte download --pubkey <publisher-npub> --relays <relay-url> --servers <blossom-url> --output ./verification
   ```

   Replace placeholders with actual deployment values; include the same `--name` for a named site. Compare SHA-256 hashes of downloaded HTML and assets against the build. Do not overwrite an existing directory.
6. For public publication, open the gateway from another client and verify HTML, assets, and routes. For a root site, `https://<publisher-npub>.nsite.lol/` is a candidate URL, not proof of availability. Named-site addressing depends on the gateway. Deliver a verified URL or state which verification failed.

## Public versus local publication

A public gateway must discover the manifest and retrieve its blobs. Use the project's selected, publicly reachable relays and Blossom servers for public publication. Do not silently add fallback destinations or publish unrelated profile metadata.

For an explicitly local test, existing services might use this configuration:

```json
{
  "relays": ["ws://127.0.0.1:4870"],
  "servers": ["http://127.0.0.1:24243"]
}
```

These are example endpoints, not services supplied by the skill. Use them only when running. A deployment exclusively to loopback addresses is local: an external gateway cannot reach those services. Waiting for propagation does not fix that. Public access needs reachable destinations and discovery, or explicitly configured replication.

Myco is an optional client for opening the verified URL. If a QR code is requested, generate it locally from that URL.

## Setup when needed

If nsyte is missing, install from the official source:

```bash
curl -fsSL https://nsyte.run/get/install.sh | bash
```

See the [installation documentation](https://nsyte.run/docs/installation) if this fails. For a new project, run `nsyte init` once and configure the selected destinations in `.nsite/config.json`. Prefer an existing NIP-46 bunker. Keep credentials out of command arguments, logs, and build files; use the configured signer or `--prompt-sec` when needed.

Run `nsyte validate` after configuration changes. It validates structure, not network reachability. Deployment needs a Blossom destination and a relay; a local Blossom server is unnecessary when another server is configured.

For preview use the project's existing command or `nsyte serve --dir ./dist`.

## Verified behavior and troubleshooting

Command options and a two-file dry run were checked with **nsyte 0.27.2**; see [validation notes](references/validation.md).

- **Empty manifest:** in the tested version, an absolute deploy path was joined to the working directory, finding zero files while returning success. Use a project-relative path and inspect file counts and manifest entries.
- **Missing assets:** check filename casing, base paths, and build contents.
- **Failed publication:** check configured services and signer errors. `nsyte status` and `nsyte debug` help diagnose problems; neither replaces retrieving files and opening the gateway.
- **Secret detected:** stop, remove it from the build, and rotate it if exposed. Rebuild before publishing.

Consult the [deploy reference](https://nsyte.run/docs/usage/commands/deploy) for current options. When the installed version differs, check relevant flags with `nsyte deploy --help`.
