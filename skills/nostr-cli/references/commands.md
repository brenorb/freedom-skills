# nostr-cli command patterns

Read this file only when the user needs raw command patterns beyond the default workflow in `SKILL.md`.

If the user also needs protocol context for `kind` numbers or NIP names mentioned here, read `references/nips-and-kinds.md`.

Use the live send and mutation examples here only after the user confirmed the final target, payload, and intended account.

## Inspect local setup

```bash
nostr version --json
nostr accounts --json
nostr relays --json
```

## Create or switch accounts

```bash
nostr login --new
nostr login
nostr switch alice
nostr switch --json
nostr accounts
nostr accounts --json
```

Use `nostr login` as a user-run terminal step for real keys. Only use `nostr login --nsec nsec1...` when the user explicitly asks the local agent to handle the secret in a local-enough setup and explicitly accepts shell-history and process-list exposure.

## Read profiles and feeds

```bash
nostr profile alice --json
nostr profile alice -n 10 --jsonl
nostr profile alice --refresh --json
nostr alice --json --limit 10
nostr alice --watch --jsonl
nostr --watch --jsonl
```

## Query events

```bash
nostr events --kinds 1 --since 1h --jsonl
nostr events --kinds 1,7 --author alice --limit 50 --json
nostr events --watch --kinds 4 --me --jsonl
nostr events --watch --kinds 1 --filter "t=bitcoin" --jsonl
nostr events --kinds 4 --since 24h --decrypt --jsonl
```

## Publish notes and replies

```bash
nostr post "Hello Nostr" --account bot-account --dry-run --json
nostr post "Hello Nostr" --account bot-account --json
echo "Hello from stdin" | nostr post --account bot-account --jsonl
nostr reply note1abc... "Great post!" --account bot-account --dry-run --json
nostr reply note1abc... "Great post!" --account bot-account --json
```

## Long-form content

```bash
nostr post -f article.md --title "My Article" --account bot-account --dry-run --json
nostr post -f article.md --title "My Article" --account bot-account
nostr post -f article.md --slug my-article --draft --account bot-account --dry-run --json
nostr post -f updated.md --slug my-article --account bot-account --json
```

## DMs

```bash
nostr dm alice "Hello" --account bot-account --json
nostr dm alice "Hello" --account bot-account --nip04 --json
echo "Automated alert" | nostr dm alice --account bot-account
nostr dm alice --watch --jsonl
nostr dm --watch --since 1h --jsonl
```

## Follow graph and aliases

```bash
nostr follow alice --account bot-account --json
nostr follow alice --account bot-account --alias al
nostr unfollow alice --account bot-account
nostr following --json
nostr following --refresh --json
nostr alias alice npub1...
nostr aliases
nostr alias rm alice
```

## Relays

```bash
nostr relays --account bot-account --json
nostr relays add wss://relay.example.com --account bot-account
nostr relays rm nos.lol --account bot-account
```

## Raw events and protocol helpers

```bash
nostr event new --kind 1 --content "Hello world" --account bot-account --dry-run --json
nostr event new --kind 7 --content "+" --tag e=<eventid> --tag p=<pubkey> --account bot-account --json
nostr nip 44
nostr nip 65
```

Prefer `nostr reply` over `nostr event new` for replies unless the user explicitly needs raw tag control.

## Generate NIP-05 data

```bash
nostr generate nip05 --address user@domain.com
nostr generate nip05 --address user@domain.com --json
```

## Sync and maintenance

```bash
nostr sync --json
nostr sync --relay nos.lol --json
nostr version --json
nostr update --json
```

Do not run `nostr update` unless the user explicitly asked to update the CLI.

## Full docs

If the user needs the complete upstream command surface or examples beyond this skill:

- CLI overview and usage examples: `https://github.com/xdamman/nostr-cli/blob/main/README.md`
- Full command reference: `https://github.com/xdamman/nostr-cli/blob/main/docs/COMMANDS.md`
- Project repo: `https://github.com/xdamman/nostr-cli`
