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

Before every deployment, run the bundled port validator proactively against the final build. Do not ask permission for this check. Resolve failures or inspect inconclusive results before publishing; never insert unused URLs to make the check pass.

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

## Validate app ports before deployment

Always run the bundled static validator against the final build before deployment:

```bash
python3 <skill-directory>/scripts/validate_app_ports.py ./dist
```

When the app uses Blossom, add `--blossom` to require HTTP(S) endpoint evidence on port `24243` as well. Resolve `<skill-directory>` to this installed skill's directory. For an app with no relay functionality, use `--no-relay`; this still runs the build check and flags conflicting literal WebSocket ports. Add `--blossom` whenever the app uses Blossom, independently of relay use. Select these options from the app functionality, never simply to silence a failure.

The script checks literal URLs in built HTML, JavaScript, and JSON. It requires a WebSocket URL on `4870` and flags other literal WebSocket ports. It prints file/line evidence without endpoint credentials, returning 0 for matching static evidence, 1 for missing/conflicting evidence, or 2 for an unreadable/invalid build.

This is not a runtime proof: comments or unused code can contain matching URLs, and computed/injected URLs may be unresolved. Other WebSocket services need manual review. HTTP URLs cannot be classified as Blossom automatically, so `--blossom` requires a matching URL but cannot rule out additional Blossom endpoints. Confirm the actual relay connection and, when applicable, an upload/download request in browser network tools. Do not bypass a failed check by inserting unused URLs.

## Named URLs, like Envelope

For a URL whose subdomain ends with a chosen site name, publish a named site:

```bash
nsyte deploy ./dist --name envelope
```

Use the same name for dry runs, updates, and downloads. Choose a new name for a new site; reusing a publisher/name pair updates that existing site. Names have 1–13 lowercase letters, digits, or hyphens and cannot end in a hyphen. The equivalent saved configuration is `"id": "envelope"` in `.nsite/config.json`.

This produces a kind-35128 manifest with `d=envelope`. On nsite.lol the URL is `https://<public-key-base36><name>.nsite.lol/`: the public key is encoded as exactly 50 lowercase base36 characters, padded with leading zeros. The suffix is the site identifier, not a mined vanity key or a purchased domain. Reuse the URL reported by the CLI and verify it.

Envelope's public deployment demonstrates this mapping:
`https://1nywmkqmtwmbl188q8gggxw8vjp62phce9ujzga9cdgtikqd2oenvelope.nsite.lol/`.
Its manifest has `d=envelope`; the preceding 50 characters encode the publisher's public key. Do not reuse that publisher or overwrite that site for a test.

If the CLI does not print the named URL, calculate it from the manifest's **public** hex key (never a private key):

```bash
node -e 'const [key,name]=process.argv.slice(1); if(!/^[0-9a-f]{64}$/i.test(key)||!/^[a-z0-9-]{1,13}$/.test(name)||name.endsWith("-"))process.exit(1); console.log("https://"+BigInt("0x"+key).toString(36).padStart(50,"0")+name+".nsite.lol/")' <public-key-hex> <site-name>
```

See upstream [named-site encoding](https://github.com/sandwichfarm/nsyte/blob/main/src/lib/nip5a.ts) for the format.

## Setup when needed

If nsyte is missing, install from the official source:

```bash
curl -fsSL https://nsyte.run/get/install.sh | bash
```

For a new project, initialize once:

```bash
nsyte init
```

Run `init` in an interactive terminal (PTY); its prompts can loop when launched without one. Finish selecting the publisher, site name, relay URLs, and Blossom URLs. A generated private key is printed once and is not saved as a usable signer by initialization: retain it securely outside the build, never in a public artifact or commit. Prefer the existing bunker flow for normal use.

Before the first deploy, ensure destinations are nonempty. In nsyte 0.27.2, `--use-fallbacks` does not fix an empty required server list. Set explicit selected relay/server URLs in the config or via `--relays` and `--servers`. `--non-interactive` still needs a configured signer; use `--prompt-sec` in a PTY when supplying a key interactively. Inspect partial server failures and verify retrieval before reporting success.

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

Substitute the actual destinations and include the same `--name` for a named site. Command options were checked with nsyte 0.27.2; consult `nsyte deploy --help` or the [deploy reference](https://nsyte.run/docs/usage/commands/deploy) when versions differ.
