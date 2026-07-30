---
name: nsyte-static-sites
description: Build, validate, and deploy static websites as Nostr nsites with the nsyte CLI. Use for static HTML, CSS, JavaScript, and asset sites that should be published through a local Nostr relay on port 4870, optionally a local Blossom server on port 24243, and handed off through an npub.nsite.lol URL or QR code. Do not use for server-side applications, APIs, databases, or other non-static deployments.
metadata:
  version: "0.1.0"
  repository: "https://github.com/sandwichfarm/nsyte"
  homepage: "https://nsyte.run"
---

# nsyte Static Sites

Use nsyte to publish a static site to the Nostr network. An nsite is not a conventional web server: its files are content-addressed blobs, usually stored on Blossom servers, and a signed Nostr manifest maps URL paths to those files. Gateways resolve the site from the publisher's npub.

This skill covers static sites only. Client-side JavaScript is allowed, including browser code that talks to a Nostr relay. Server-side rendering, API routes, server actions, databases, private backends, and processes that must stay running are out of scope. If the requested app needs those capabilities, stop and explain that it must be made static first.

## Build the site

1. Identify the project's static build command and its output directory. Prefer the project's existing build tool and output convention.
2. Run the build and inspect the output before publishing. It must contain the complete browser payload: HTML, CSS, JavaScript, images, fonts, and other public assets.
3. Check that asset URLs work from the deployed site. Prefer relative or root-relative paths, preserve filename casing, and make sure the output has an `index.html`. For a client-side single-page app, configure a fallback to `/index.html` if the gateway needs one.
4. Keep secrets out of the output. Do not deploy private keys, `.env` files, credentials, source maps containing secrets, or unpublished data. Run `nsyte scan` when available before deployment.

When the user says to “vibe” the app, iterate against the built static output and keep the app runnable without a server runtime. For local preview, use the project's preview command or:

```bash
nsyte serve
```

## Install and configure nsyte

Install nsyte from the official site:

```bash
curl -fsSL https://nsyte.run/install.sh | bash
```

If the installer reports a problem, use the [official installation documentation](https://nsyte.run/docs/installation/) and then return to this workflow. Do not substitute an untrusted installer.

Initialize the project once:

```bash
nsyte init
```

Configure the local services in `.nsite/config.json` or through `nsyte config`:

```json
{
  "relays": ["ws://127.0.0.1:4870"],
  "servers": ["http://127.0.0.1:24243"]
}
```

Use the relay on port `4870` for Nostr events. Include the Blossom server on port `24243` only when the local workflow needs Blossom storage. If either local service is unavailable, report that clearly; do not silently publish to a different service. Keep the project key or bunker configuration private, and prefer a NIP-46 bunker when the user already has one.

Validate configuration before uploading:

```bash
nsyte validate
```

## Deploy

Deploy the directory produced by the build, not the source tree:

```bash
nsyte deploy [path-to-dist]
```

Replace `[path-to-dist]` with the actual output path, for example `./dist`. If the command supports a dry run or validation mode in the installed version, use it before the first real upload. Otherwise, run `nsyte scan` and `nsyte validate` first.

After deployment:

1. Capture the published npub and site information printed by nsyte.
2. Confirm that the public gateway URL is `https://[npub].nsite.lol/` and open it to verify the entry page, asset loading, and client-side interactions.
3. Check propagation with `nsyte status` if the site is not immediately available. A relay or Blossom service may need time to receive the manifest or blobs.
4. Give the user the complete URL. They can paste it into Myco.

Example handoff:

```text
https://[npub].nsite.lol/
```

For a QR handoff, encode the complete URL at [QRCode Monkey](https://www.qrcode-monkey.com/), download or display the QR code, and scan it with Myco. Warn the user before sending a sensitive or unpublished URL to an external QR service; use a local QR generator instead when privacy matters.

## Troubleshoot common failures

- **Build output is missing or empty:** run the project's build command and deploy its actual output directory.
- **The page loads without styles or scripts:** inspect URL casing and base paths; static gateways do not rewrite arbitrary asset paths.
- **Client-side routes return not found:** add the nsite fallback to `/index.html`, or use hash-based routing.
- **Deployment cannot publish events:** check that `ws://127.0.0.1:4870` is running and reachable, then run `nsyte status` or `nsyte debug`.
- **Files are not available:** check that the configured Blossom server is reachable at `http://127.0.0.1:24243`, then retry with `nsyte status`.
- **A secret appears in the build:** stop, remove it from source and build artifacts, rotate it if it was exposed, and do not deploy until the output is clean.

For current command options, consult the [nsyte documentation](https://nsyte.run/docs/) and the [nsite protocol overview](https://nsite.run/).
