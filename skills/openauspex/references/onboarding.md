# openauspex onboarding

Read this file only when the direct `auspex` command path fails or the user needs first-time setup.

## Prerequisites

- Node 20 or newer
- network access to the chosen Nostr relays
- for operator workflows, a Nostr signing key available as `CANARY_NSEC` or `CANARY_SECRET_KEY`

Check the environment:

```bash
node --version
npx -y @openauspex/cli --help
```

If Node is missing or too old, install or upgrade Node first.

## Install choices

Ad hoc usage:

```bash
npx -y @openauspex/cli --help
```

Repeated operational usage, cron, or systemd:

```bash
npm install -g @openauspex/cli
auspex --help
```

## Bootstrap a canary workspace

Create a dedicated directory and scaffold the config there:

```bash
mkdir -p /path/to/canary
cd /path/to/canary
npx -y @openauspex/cli init
```

Edit `canary.config.json` before publishing. The config needs:

- `relays`
- `canaryId`
- a `definition` block for operator-side publishing

`bitcoin.explorers` has sensible defaults, so override it only when the user wants different explorers.

## Minimal first publish flow

Generate or provide the signer key:

```bash
npx -y @openauspex/cli keygen
export CANARY_NSEC=nsec1...
```

Publish the definition, then the first attestation:

```bash
npx -y @openauspex/cli define
npx -y @openauspex/cli attest
```

Later, after the OpenTimestamps proof has confirmed on Bitcoin:

```bash
npx -y @openauspex/cli upgrade
```

For reminder-only scheduling, the command still wants a definition pubkey context:

```bash
npx -y @openauspex/cli remind --pubkey <author-hex>
```

## Minimal watcher flow

If the watcher does not author the canary, use the operator's author pubkey:

```bash
npx -y @openauspex/cli inspect --pubkey <author-hex>
npx -y @openauspex/cli check --pubkey <author-hex>
npx -y @openauspex/cli notify --pubkey <author-hex>
```

## Common failures

- `canary.config.json already exists; not overwriting`
  Create a new working directory or use the existing config.
- `config has no definition block`
  Fill in the `definition` section before `define`.
- `no secret key`
  Export `CANARY_NSEC` or `CANARY_SECRET_KEY`, or pass `--nsec`.
- `need a definition pubkey`
  Pass `--pubkey`, set `definitionPubkey` in the config, or export `CANARY_NSEC`.
- `no pending stamps`
  `upgrade` has nothing ready yet; retry later.

## Safety notes

- Prefer supplying `CANARY_NSEC` through a secure env source or temporary shell context instead of `--nsec ...`. Avoid typing secrets directly into interactive shell history.
- Use `remind --pubkey <author-hex>` for reminder automation; `CANARY_NSEC` is only one way to supply or derive that pubkey context.
- Treat `notify` and `remind` as outbound network actions whenever their config or flags use webhook channels.

## Package-manager noise

The first `npx -y @openauspex/cli ...` run can print npm deprecation warnings from transitive dependencies. Treat those as package-manager noise unless the `auspex` command itself exits non-zero.
