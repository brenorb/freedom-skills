# openauspex commands

Read this file only when `SKILL.md` is not enough.

## CLI entrypoints

Ad hoc:

```bash
npx -y @openauspex/cli --help
```

Global install:

```bash
npm install -g @openauspex/cli
auspex --help
```

## Operator workflow

Create keys:

```bash
npx -y @openauspex/cli keygen
export CANARY_NSEC=nsec1...
```

Scaffold config:

```bash
npx -y @openauspex/cli init
```

Publish the canary definition:

```bash
npx -y @openauspex/cli define
```

Publish an attestation with all clauses affirmed:

```bash
npx -y @openauspex/cli attest
```

Publish an attestation with an explicit clause list:

```bash
npx -y @openauspex/cli attest --affirm no-secret-order,keys-undisclosed
```

Publish an attestation without OpenTimestamps stamping:

```bash
npx -y @openauspex/cli attest --no-stamp
```

Signal by dropping one or more clauses:

```bash
npx -y @openauspex/cli attest --drop no-secret-order
npx -y @openauspex/cli attest --drop no-secret-order,no-backdoor
```

Upgrade pending OpenTimestamps proofs later:

```bash
npx -y @openauspex/cli upgrade
```

Inspect local pending stamp state:

```bash
npx -y @openauspex/cli status
```

Operator reminder automation:

```bash
npx -y @openauspex/cli remind --pubkey <author-hex>
npx -y @openauspex/cli remind --pubkey <author-hex> --lead 259200,86400,3600
npx -y @openauspex/cli remind --pubkey <author-hex> --webhook https://ntfy.sh/my-canary
```

## Watcher workflow

Single health check:

```bash
npx -y @openauspex/cli check --pubkey <author-hex>
```

Foreground watcher loop:

```bash
npx -y @openauspex/cli watch --pubkey <author-hex> --interval 300
```

Inspect raw events:

```bash
npx -y @openauspex/cli inspect --pubkey <author-hex>
npx -y @openauspex/cli inspect --pubkey <author-hex> --json
```

Verify the latest attestation's OpenTimestamps proof:

```bash
npx -y @openauspex/cli verify --pubkey <author-hex>
npx -y @openauspex/cli verify --pubkey <author-hex> --att <attestation-id>
npx -y @openauspex/cli verify --pubkey <author-hex> --tree
npx -y @openauspex/cli verify --pubkey <author-hex> --out /tmp/latest-canary.ots
```

Cron-friendly state-change alerting:

```bash
npx -y @openauspex/cli notify --pubkey <author-hex>
npx -y @openauspex/cli notify --pubkey <author-hex> --interval 300
npx -y @openauspex/cli notify --pubkey <author-hex> --state /path/to/notify-state.json
npx -y @openauspex/cli notify --pubkey <author-hex> --webhook https://ntfy.sh/my-canary
```

## Config notes

- The default config path is `canary.config.json`.
- Use `-c /path/to/canary.config.json` when not running from the canary directory.
- The default pending stamp store is `.openauspex/pending.json`.
- The default notification state path is `.openauspex/notify-state.json`.
- `definitionPubkey` is for watcher-side monitoring of a canary you did not author yourself.
- First-run `npx` executions can print npm deprecation warnings from transitive dependencies even when `auspex` itself is working.
- `notify` and `remind` are outbound network actions whenever their config or flags use webhook channels.
