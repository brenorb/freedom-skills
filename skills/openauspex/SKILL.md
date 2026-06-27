---
name: openauspex
description: "Use this skill when the user wants to publish, inspect, monitor, verify, or automate a Nostr warrant canary with OpenAuspex, including Bitcoin freshness anchoring, OpenTimestamps upgrades, watcher alerts, and operator reminder workflows."
---

# openauspex

Use the published `auspex` CLI from `@openauspex/cli` to operate or monitor Nostr warrant canaries.

Prefer the direct command that matches the user's goal first. Only fall back to setup or environment checks if that command fails or the canary workspace is not ready yet.

## Default workflow

1. Match the user's goal to the direct command first:

```bash
# create a signer keypair
npx -y @openauspex/cli keygen

# bootstrap a new canary workspace
npx -y @openauspex/cli init

# operator workflow
export CANARY_NSEC=nsec1...
npx -y @openauspex/cli define
npx -y @openauspex/cli attest
npx -y @openauspex/cli upgrade
npx -y @openauspex/cli status
npx -y @openauspex/cli remind --pubkey <author-hex>

# watcher workflow
npx -y @openauspex/cli check --pubkey <author-hex>
npx -y @openauspex/cli inspect --pubkey <author-hex>
npx -y @openauspex/cli verify --pubkey <author-hex>
npx -y @openauspex/cli notify --pubkey <author-hex>
npx -y @openauspex/cli watch --pubkey <author-hex> --interval 300
```

2. If the command fails because the CLI is missing, Node is too old, `canary.config.json` is missing, or the user needs first-time setup, read `references/onboarding.md`.
3. For operator publishing, work from a dedicated canary directory so `canary.config.json` and `.openauspex/` state stay together. Use `-c /path/to/canary.config.json` when the config lives elsewhere.
4. For the first publish flow, run `define`, then `attest`, then come back later for `upgrade` once the OpenTimestamps proof has Bitcoin confirmations.
5. For ongoing monitoring, prefer `notify` and `remind` for one-shot scheduled runs. Use `watch` only when the user explicitly wants a foreground loop.
6. If the user needs raw command patterns beyond the defaults here, read `references/commands.md`.

## Defaults

- Prefer `npx -y @openauspex/cli ...` for ad hoc use.
- Prefer `npm install -g @openauspex/cli` only when the user wants cron, systemd, or repeated operational use.
- Prefer one working directory per canary so the config file and `.openauspex/` state do not bleed across unrelated canaries.
- Prefer `inspect` before `watch`, `notify`, or `verify` when the user is unsure which canary or pubkey they are targeting.
- Prefer `notify` for watcher-side automation and `remind` for operator-side automation.
- Prefer supplying `CANARY_NSEC` through a secure env source or temporary shell context instead of `--nsec` on the command line. Avoid typing secrets directly into interactive shell history.
- Prefer `attest --affirm <id,id,...>` only when the user wants to affirm a narrowed subset explicitly instead of using the definition defaults.
- Prefer `attest --drop <clause-id>` only when the user explicitly intends to signal that a clause is no longer affirmed.
- Prefer `remind --pubkey <author-hex>` for scheduled reminder workflows; `CANARY_NSEC` is only one way to derive that pubkey.
- Prefer `--pubkey <author-hex>` for watcher commands when the canary is not authored by the local operator.

## Safety rules

- Treat `define`, `attest`, and `upgrade` as external write actions to public relays.
- Treat `notify` and `remind` as outbound network actions whenever their config or flags use webhook channels.
- Treat `keygen` as secret creation. Show the generated `nsec` once, tell the user to store it safely, and do not repeat it back unnecessarily.
- Confirm the exact canary directory, config, and target pubkey before any publish or long-running monitor action.
- Confirm the clause set before `attest --drop ...`, because dropping a clause is the actual canary signal.
- Do not leak `CANARY_NSEC` values in chat output, logs, screenshots, or saved notes.
- If the user wants watcher-only inspection, do not ask for or use a signing key.

## Gotchas

- OpenAuspex requires Node 20+.
- `init` writes `canary.config.json` and refuses to overwrite an existing file.
- `define` needs a populated `definition` block in the config.
- `check`, `watch`, `inspect`, `verify`, and `notify` need a definition pubkey from `--pubkey`, `definitionPubkey` in the config, or `CANARY_NSEC`.
- `status` reports local config and pending stamp state, not the remote canary health verdict.
- `attest --no-stamp` skips OpenTimestamps stamping for that attestation.
- `upgrade` can legitimately report that proofs are still pending; rerun it later after Bitcoin confirmations.
- `verify --tree` and `verify --out <path>` are for proof inspection and export when the default summary is not enough.
- `notify --interval <seconds>` keeps polling in the foreground instead of running once like a cron-friendly check.
- First-run `npx -y @openauspex/cli ...` executions can print npm deprecation warnings from transitive dependencies even when the command itself succeeds.
- `notify` and `remind` de-duplicate through `.openauspex/notify-state.json` unless `--state` overrides the path.
- `watch` keeps running until stopped.
