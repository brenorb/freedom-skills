---
name: nsyte-static-sites
description: Publish or update static HTML, CSS, JavaScript, and assets on Nostr using nsyte and Blossom storage. Use for deploying built sites and verifying retrieval with configured public or local services. Server-side runtimes require separate hosting.
metadata:
  version: "0.1.0"
  repository: "https://github.com/sandwichfarm/nsyte"
  homepage: "https://nsyte.run"
---

# nsyte Static Sites

```bash
nsyte deploy ./dist
```

Deploy the static build from the project root, using its existing configuration and signer. nsyte hosts files, not server-side processes. For changes to a published site, read [update.md](references/update.md).

## Deploy

1. Build the app and preview it with the project's command or `nsyte serve --dir ./dist`.
2. **Always validate the final build before publishing, without asking:**

   ```bash
   python3 <skill-directory>/scripts/validate_app_ports.py ./dist
   ```

   Add `--no-relay` if the app has no relay functionality; add `--blossom` whenever it uses Blossom. Resolve `<skill-directory>` to this skill's location.
3. Run `nsyte deploy ./dist --dry-run`; confirm the file count and paths. Use a relative build path: nsyte 0.27.2 can produce an empty manifest from an absolute path. Keep the secrets scan enabled.
4. Deploy, then open the public URL and test assets and interactions. Report upload/relay failures and anything unverified. For an SPA, add `--fallback index.html` and test a nested route.

## Runtime ports

The app's Nostr relay must use `4870`; its Blossom service, if used, must use `24243`. Resolve the host/protocol from the target environment and keep endpoints configurable. Loopback means the **visitor's device**. Check HTTPS, WebSocket, and CORS compatibility in the intended browser.

These are **app runtime** endpoints, separate from the CLI's publication relays/servers in `.nsite/config.json`. Reuse the configured publication destinations; the public gateway must be able to reach them.

**Stop deployment of the feature if a required runtime endpoint is unavailable or uses the wrong port.** Do not substitute port `443`, omit required validator flags, or insert unused URLs to pass.

The validator scans literal URLs, not actual traffic. Computed URLs and unrelated WebSockets need manual review; matching strings do not prove a connection works. It also cannot identify every Blossom URL. Verify real requests in the browser. Manual review does not waive a confirmed port mismatch.

## Named URLs, like Envelope

```bash
nsyte deploy ./dist --name <site-name>
```

Use the same name for dry runs, updates, and downloads. Names contain 1–13 lowercase letters, digits, or hyphens, with no trailing hyphen. Save it as `"id"` in `.nsite/config.json` if desired.

Envelope used `--name envelope`: its URL suffix comes from the site name, not vanity-key mining. Use your own publisher/name for a new site. **Same publisher + name = same site and URL.** Preserve the root configuration for unnamed sites.

On nsite.lol, named URLs are `https://<public-key-base36><name>.nsite.lol/`, with a 50-character, zero-padded lowercase base36 public key. Prefer the CLI's URL; if absent, calculate from the manifest's **public hex key**:

```bash
node -e 'const [key,name]=process.argv.slice(1); if(!/^[0-9a-f]{64}$/i.test(key)||!/^[a-z0-9-]{1,13}$/.test(name)||name.endsWith("-"))process.exit(1); console.log("https://"+BigInt("0x"+key).toString(36).padStart(50,"0")+name+".nsite.lol/")' <public-key-hex> <site-name>
```

Root sites can use `https://<publisher-npub>.nsite.lol/`. Verify either URL before reporting success. [Upstream named-site format](https://github.com/sandwichfarm/nsyte/blob/main/src/lib/nip5a.ts).

## Setup only when needed

Install if missing:

```bash
curl -fsSL https://nsyte.run/get/install.sh | bash
```

For a new project, run `nsyte init` in a PTY; non-interactive prompts can loop. Configure the publisher and nonempty relay/server destinations. A generated key is printed once, not saved as a usable signer; retain it securely outside the build and logs. Prefer an existing NIP-46 bunker, or use `--prompt-sec` in a PTY. Keep secrets out of command arguments and commits.

In nsyte 0.27.2, `--use-fallbacks` does not fix empty server lists: set destinations in config or with `--relays`/`--servers`. `--non-interactive` still requires a signer. `nsyte validate` checks config structure, not reachability.

## Retrieval problems

Check upload/relay errors and gateway discovery. To verify stored files, download to a fresh directory and compare hashes with the build:

```bash
nsyte download --pubkey <publisher-npub> --relays <relay-url> --servers <blossom-url> --output ./verification
```

Include `--name <site-name>` for named sites. Check `nsyte deploy --help` for version differences; these commands were tested with 0.27.2. [CLI documentation](https://nsyte.run/docs/usage/commands/deploy).
