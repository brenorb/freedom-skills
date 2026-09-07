---
name: nsyte-static-sites
description: Publish or update static HTML, CSS, JavaScript, and assets on Nostr using nsyte and Blossom storage. Use for deploying built sites and verifying retrieval with configured public or local services. Server-side runtimes require separate hosting.
metadata:
  version: "0.1.0"
  repository: "https://github.com/sandwichfarm/nsyte"
  homepage: "https://nsyte.run"
---

# nsyte Static Sites

Publish static websites with the [nsyte CLI](https://nsyte.run/). An [nsite](https://nsite.run/) stores browser files on Blossom servers and publishes signed Nostr events mapping site paths to those files.

## Default workflow

For an existing build, deploy from the project root:

```bash
nsyte deploy ./dist
```

Replace `./dist` with the project's actual relative output directory. Reuse its existing nsyte configuration and signer. Installation and initialization are fallbacks, not steps to repeat on every deploy.

1. If asked to build or change the app, use the existing framework and build command. Produce static HTML, CSS, JavaScript, and assets. Client-side apps can use Nostr and other external services; nsyte does not host server-side processes or databases.
2. When the app needs Nostr or Blossom, configure its runtime connections as described below. A static page needs neither connection in its application code.
3. Build and preview the output using the project's preview command, or `nsyte serve --dir ./dist`. Check the entry page and referenced assets. Deploy the output directory, not the repository or credentials.
4. For a first publication or changed build/destination, inspect a preview:

   ```bash
   nsyte deploy ./dist --dry-run
   ```

   Confirm the expected file count and manifest paths. Then run the deploy command above. Keep the default secrets scan enabled. For a single-page app requiring a fallback, use `nsyte deploy ./dist --fallback index.html` and check a nested route afterward.
5. Inspect the upload and relay results, then open the published site and check assets and relevant interactions. Return the URL and any remaining verification failure. For a root site, `https://<publisher-npub>.nsite.lol/` is a candidate gateway URL; verify it before calling the site accessible. Named-site URLs depend on the gateway.

## App connections: relay :4870 and Blossom :24243

The supplied app-building instructions call for a relay on port `4870` and, when the app uses Blossom, a server on port `24243`. Treat these as connections used by the app at runtime. Resolve the host and protocol from the target environment or existing app configuration; the port alone is not a complete URL.

- Preserve these ports when building for that environment. Keep endpoint URLs configurable so another environment can supply its own services.
- Use loopback only when the target browser is meant to access services on its own device. In a deployed app, `127.0.0.1` refers to the visitor's device, not the developer's computer.
- Respect browser HTTPS/WebSocket and cross-origin restrictions when verifying connections. Test the app in the intended browser or client.
- Do not copy these ports into `.nsite/config.json` merely because the app uses them. App runtime connections and the CLI's publication destinations are separate settings; they may share services only when explicitly configured that way.

For public publication, the selected gateway must be able to discover the manifest and fetch the blobs. Reuse the project's publication relays and Blossom servers; do not silently substitute services. Loopback-only publication requires a local client or a configured replication arrangement for external access.

## Setup when needed

If nsyte is missing, install from the official source:

```bash
curl -fsSL https://nsyte.run/get/install.sh | bash
```

For a new project, initialize once:

```bash
nsyte init
```

Configure the selected publication relays, Blossom servers, and signer in `.nsite/config.json`. Prefer an existing NIP-46 bunker; keep credentials out of command arguments and build files. Use the configured signer or `--prompt-sec` when needed. After configuration changes, `nsyte validate` checks structure, not network reachability.

See the [installation guide](https://nsyte.run/docs/installation) if setup fails.

## Troubleshooting

- **Zero files despite success:** nsyte 0.27.2 was observed joining an absolute deployment path to the current directory and emitting an empty manifest. Use a relative path and inspect the file count.
- **Page works but app does not:** inspect runtime relay/Blossom connections separately from the upload result. Check endpoint host, protocol, browser restrictions, and service availability.
- **Missing assets or routes:** check casing, base paths, build contents, and the SPA fallback.
- **Failed publication:** inspect signer and configured destination errors; `nsyte status` or `nsyte debug` can help. Do not treat a constructed URL as a successful deployment.

For a first end-to-end acceptance test or suspected storage corruption, download into a fresh directory and compare HTML/asset hashes with the build:

```bash
nsyte download --pubkey <publisher-npub> --relays <relay-url> --servers <blossom-url> --output ./verification
```

Substitute the actual destinations and include the same `--name` for a named site. See [validation notes](references/validation.md) for tested behavior and the remaining live-publication check. Command options were checked with nsyte 0.27.2; consult `nsyte deploy --help` or the [deploy reference](https://nsyte.run/docs/usage/commands/deploy) when versions differ.
