# Freedom-Tech Automation Inventory

As of 2026-05-14.

This document answers a narrower question than the landscape scan: which products already have real automation surfaces, existing AI integrations, or obvious skill-building interfaces?

## Quick Read

Best first-wave skill targets:

1. `btcpay-greenfield`
2. `nostr-ops`
3. `nwc-wallet`
4. `cashu-cli`
5. `simplex-bot`
6. `matrix-community-ops`
7. `bitcoin-core-readonly`

Best second-wave targets:

1. `fedimint-client`
2. `signal-signald`
3. `lnbits`
4. `gpg-openpgp`
5. `white-noise-core`

Defer for now:

1. `keet`
2. `briar`
3. `bitchat`
4. `nowhere`
5. standalone `rsa`

## 1. What Already Exists

### Existing packaged skills or agent integrations

| Product | Existing integration | Link | Notes |
| --- | --- | --- | --- |
| Signal | Local `signal-cli` skill in this repo on `main` | Upstream surface: [AsamK/signal-cli](https://github.com/AsamK/signal-cli) | Already proves the pattern: sync, resolve recipients, send safely. |
| Nostr | MCP server | [AustinKelsay/nostr-mcp-server](https://github.com/AustinKelsay/nostr-mcp-server) | Real MCP packaging for profiles, notes, keys, and NIP search. |
| NWC / Lightning | Alby MCP | [getAlby/mcp](https://github.com/getAlby/mcp) | Strong packaged MCP around NWC, LNURL, and related Lightning flows. |
| Bitcoin | Community MCPs | [runeape-sats/bitcoin-mcp](https://github.com/runeape-sats/bitcoin-mcp), [AbdelStark/bitcoin-mcp](https://github.com/AbdelStark/bitcoin-mcp) | Not first-party, but enough exists to show demand and feasibility. |
| mesh-llm | Built-in skill material | [Mesh-LLM/mesh-llm](https://github.com/Mesh-LLM/mesh-llm) | Support infra, not core freedom tech. |
| Crabbox | Built-in skill material | [openclaw/crabbox](https://github.com/openclaw/crabbox) | Same conclusion as mesh-llm: useful infra around the skill stack. |

### High-quality low-level automation surfaces with no good Freedom Skill yet

| Product | Strongest surface | Link | Buildability |
| --- | --- | --- | --- |
| Bitcoin Core | JSON-RPC and `bitcoin-cli` | [RPC docs](https://bitcoincore.org/en/doc/26.0.0/) | `Very high` |
| HWI | Hardware wallet CLI/API | [bitcoin-core/HWI](https://github.com/bitcoin-core/HWI) | `High` |
| BDK | Wallet SDK and CLI | [bitcoindevkit/bdk](https://github.com/bitcoindevkit/bdk) | `High` |
| LND | gRPC / REST | [lightningnetwork/lnd](https://github.com/lightningnetwork/lnd) | `Very high` |
| Core Lightning | JSON-RPC and plugins | [ElementsProject/lightning](https://github.com/ElementsProject/lightning) | `Very high` |
| BTCPay Server | Greenfield API | [BTCPay docs](https://docs.btcpayserver.org/CustomIntegration/) | `Very high` |
| LNbits | HTTP API and extensions | [lnbits/lnbits](https://github.com/lnbits/lnbits) | `High` |
| Cashu | Nutshell CLI / mint server | [cashubtc/nutshell](https://github.com/cashubtc/nutshell) | `Very high` |
| Cashu | CDK CLI / mintd / gRPC | [cashubtc/cdk](https://github.com/cashubtc/cdk) | `High` |
| Fedimint | `fedimint-cli` and client RPC | [fedimint/fedimint](https://github.com/fedimint/fedimint) | `High` |
| Nostr | `nak` CLI | [fiatjaf/nak](https://github.com/fiatjaf/nak) | `Very high` |
| Nostr | SDKs and relay implementations | [rust-nostr](https://github.com/rust-nostr/nostr), [strfry](https://github.com/hoytech/strfry) | `High` |
| Signal | `signald` | [signald docs](https://signald.org/articles/getting-started/) | `High` |
| SimpleX | Terminal CLI + local WebSocket bot API | [simplex-chat/simplex-chat](https://github.com/simplex-chat/simplex-chat) | `Very high` |
| Matrix | SDKs and bot tooling | [matrix-rust-sdk](https://github.com/matrix-org/matrix-rust-sdk), [matrix-commander](https://github.com/8go/matrix-commander) | `Very high` |
| White Noise | Rust core + CLI binaries | [marmot-protocol/whitenoise-rs](https://github.com/marmot-protocol/whitenoise-rs) | `Medium` |
| GPG / OpenPGP | `gpg` CLI | [GnuPG docs](https://www.gnupg.org/documentation/manuals/gnupg/Invoking-GPG.html) | `Very high` |
| GPG / OpenPGP | `sq` CLI / Sequoia | [Sequoia PGP](https://github.com/sequoia-pgp/sequoia) | `High` |

### Weak or missing automation surfaces

| Product | Why it is weak today | Judgment |
| --- | --- | --- |
| Keet | App-first product; no obvious stable automation surface. | Do not build a Keet skill first. |
| Briar | Strong mission fit, weak public automation surface. | Watch only. |
| Bitchat | Interesting protocol and codebase, but still app-centric and security-sensitive. | Watch only. |
| Nowhere | Strong publishing idea, weak public SDK/CLI/API surface. | Watch only. |
| standalone RSA | Too primitive and misuse-prone. | Fold into GPG/OpenPGP or OpenSSL ops. |

## 2. Recommendations by Product Area

### Build now

| Skill | Why now |
| --- | --- |
| `btcpay-greenfield` | Stable merchant API, high real-world leverage, clearly non-custodial. |
| `nostr-ops` | Strong CLI/SDK/MCP ecosystem and central to the Bitcoin-adjacent stack. |
| `nwc-wallet` | Best current programmable wallet surface for agents. |
| `cashu-cli` | Strong wallet and mint CLI surface; high privacy relevance. |
| `simplex-bot` | One of the best un-packaged freedom-tech bot surfaces available. |
| `matrix-community-ops` | Bots, bridges, rooms, and moderation all map well to skills. |
| `bitcoin-core-readonly` | Safe and useful entry point into node-aware skills. |

### Build soon

| Skill | Why later |
| --- | --- |
| `fedimint-client` | Buildable, but ecosystem is still moving quickly. |
| `signal-signald` | Richer than raw `signal-cli`, but heavier to operate. |
| `lnbits` | Good wallet/account experimentation layer once the core stack is covered. |
| `gpg-openpgp` | Valuable, but should stay tightly scoped around sign/verify/encrypt/decrypt. |
| `white-noise-core` | Promising, but current surface is still library-first. |
| `zeus-helper` | Useful wallet/node surface, but after core protocols and merchant rails. |
| `boltz-swaps` | Important operationally, but best after Core/Lightning/BTCPay coverage exists. |

### Watchlist

| Candidate | Why wait |
| --- | --- |
| `nowhere` | Interesting architecture, but current public automation surface is weak. |
| `bitchat` | High-upside for protests/disasters, but too immature and app-centric. |
| `keet` | Better to target Holepunch primitives than the Keet app itself. |
| `session` | Buildable enough to experiment with, but lower priority. |
| `mesh-llm` | Support infra for sovereign agents, not a first-wave product skill. |
| `crabbox` | Same as mesh-llm: useful around Freedom Skills, not the core roadmap. |

## 3. Specific Calls on the Added Items

### `gpg`

Yes. This should become a candidate Freedom Skill.

Good scope:

- key generation
- sign
- verify
- encrypt
- decrypt
- import/export
- release verification

Bad scope:

- “teach all of OpenPGP”
- broad trust-model theory without a concrete workflow

### `rsa`

No as a standalone skill.

The right abstraction is:

- `gpg-openpgp`, if the task is human-facing secure communications or release verification
- tightly-scoped OpenSSL operations, if the task is infrastructure compatibility

### `mesh-llm`

Useful, but as support infrastructure for sovereign/private agent compute rather than freedom tech itself.

### `crab box`

Useful, but the same conclusion as `mesh-llm`: support infrastructure, not a core Freedom Skill product area.

### `nowhere`

Interesting and worth tracking. Today it looks more like a watchlist item than a near-term skill target because the public automation surface is still weak compared with BTCPay, Nostr, Cashu, Matrix, or SimpleX.

## 4. Bottom Line

The biggest gap is not protocol maturity. It is packaging maturity.

Bitcoin Core, BTCPay, Cashu, Fedimint, Nostr, NWC, SimpleX, Matrix, and GPG all already have enough surface area to support serious agent skills. The opportunity for Freedom Skills is to package those interfaces into safe, opinionated workflows before someone else does it badly.
