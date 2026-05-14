# Freedom-Tech Landscape

As of 2026-05-14.

This is the working landscape scan for Freedom Skills. It is opinionated on purpose: the goal is to identify what is important enough to deserve skill coverage, not to produce an encyclopedic list.

## Executive Take

The center of gravity is still:

1. Bitcoin Core and wallet/node primitives.
2. Lightning infrastructure and payment protocols.
3. Cashu and Fedimint.
4. Nostr as identity, distribution, messaging, and wallet-connect fabric.
5. Merchant rails such as BTCPay Server, LNbits, Alby Hub, and Boltz.

The strongest adjacent layer is censorship-resistant communications and publishing that can pair naturally with Bitcoin:

- White Noise
- Signal
- SimpleX
- Matrix
- Bitchat
- Nowhere
- Keet

Supporting sovereignty infrastructure also matters, but it should not distract from the Bitcoin-first roadmap:

- GPG / OpenPGP
- mesh-llm
- Crabbox
- RSA-based tooling as a sub-surface, not a product track

## 1. Bitcoin Monetary Stack

### Base-layer and wallet primitives

| Project / protocol | Why it matters | Skill angle | Priority |
| --- | --- | --- | --- |
| [Bitcoin Core](https://bitcoincore.org/) | Root of trust for sovereign Bitcoin operations. | Node setup, health checks, RPC, descriptors, PSBT, release verification, Tor. | `Build now` |
| [Bitcoin Dev Kit](https://bitcoindevkit.org/) | Best builder surface for scriptable wallet flows. | Wallet scaffolding, descriptor ops, tx building, recovery flows. | `Build soon` |
| [HWI](https://github.com/bitcoin-core/HWI) | Standard bridge to hardware wallets. | Device discovery, sign flows, multisig setup review. | `Build soon` |
| [Silent Payments](https://silentpayments.xyz/) | Important privacy upgrade for static receive identifiers. | Identifier generation, compatibility checks, receive guidance. | `Watch closely` |
| [Payjoin](https://payjoin.org/) | Practical spending privacy improvement. | Compatibility checks, merchant receive flows, fallback logic. | `Watch closely` |

### Lightning nodes, SDKs, and payment protocols

| Project / protocol | Why it matters | Skill angle | Priority |
| --- | --- | --- | --- |
| [LND](https://docs.lightning.engineering/lightning-network-tools/lnd) | Common Lightning backend in wallets and services. | Install, channels, invoices, payments, backups, watchtowers. | `Build now` |
| [Core Lightning](https://docs.corelightning.org/) | Very strong UNIX-style automation surface. | Node provisioning, plugin ops, BOLT 12, remote admin. | `Build now` |
| [Lightning Dev Kit](https://lightningdevkit.org/) | Best fit for agent-built Lightning apps. | App scaffolding, storage, routing, embedded Lightning. | `Build soon` |
| [LNURL](https://github.com/lnurl/luds) | Still the main Lightning glue layer. | Parse, resolve, pay, withdraw, auth, fallback handling. | `Build now` |
| [BOLT 12](https://bolt12.org/) | Reusable payment requests and better receiver privacy. | Offer generation, compatibility detection, fallback logic. | `Build soon` |
| [Boltz](https://docs.boltz.exchange/) | Core bridge between on-chain and Lightning. | Swap quoting, swap execution, restore/refund handling. | `Build soon` |

### Ecash and federated custody

| Project / protocol | Why it matters | Skill angle | Priority |
| --- | --- | --- | --- |
| [Cashu](https://docs.cashu.space/) | Best current private bearer-payment primitive on Bitcoin. | Mint discovery, mint risk scoring, send/receive/redeem flows. | `Build now` |
| [Fedimint](https://fedimint.org/) | Makes Bitcoin UX more social and community-custodial. | Federation join/recovery, guardian ops, invite parsing. | `Build now` |
| [Fedi](https://www.fedi.xyz/) | Most visible consumer packaging of Fedimint ideas. | Onboarding, mini-app support, chat + payments playbooks. | `Build soon` |
| [Minibits](https://www.minibits.cash/) | Shows where ecash, Nostr, and mobile UX converge. | Wallet ops, Nutzaps, NWC wiring, mint migration. | `Watch closely` |

### Merchant and operational rails

| Project / protocol | Why it matters | Skill angle | Priority |
| --- | --- | --- | --- |
| [BTCPay Server](https://docs.btcpayserver.org/) | Canonical non-custodial merchant stack. | Deployment, stores, Greenfield API, POS, reconciliation. | `Build now` |
| [LNbits](https://docs.lnbits.org/) | Great experimentation and wallet-partition layer. | Wallet provisioning, extensions, vouchers, paywalls, APIs. | `Build soon` |
| [Alby Hub / NWC tooling](https://guides.getalby.com/developer-guide/developer-guide/nostr-wallet-connect-api) | Lowers the barrier to programmable wallet access. | NWC setup, budgeted permissions, app registration. | `Build now` |
| [Blink](https://blink.sv/en/about) | Important for merchant onboarding and circular economies. | Merchant flows, POS support, onboarding playbooks. | `Build soon` |
| [AQUA](https://aquawallet.io/) | Relevant for Bitcoin + Liquid + stablecoin mobility. | Cross-rail guidance and recovery/support flows. | `Watch closely` |
| [ZEUS](https://blog.zeusln.com/about/) | Strong node-control and self-custody surface. | Node pairing, NWC, swaps, advanced wallet ops. | `Build soon` |
| [Phoenix](https://acinq.co/blog/phoenix-splicing-update) | Excellent self-custodial Lightning UX reference. | Liquidity explanation, splice flows, user support. | `Build soon` |

## 2. Nostr as the Coordination Fabric

Nostr is no longer just a social protocol. It is the main identity and coordination layer around Lightning-native money, wallet delegation, creator payments, and censorship-resistant distribution.

| Project / protocol | Why it matters | Skill angle | Priority |
| --- | --- | --- | --- |
| [Nostr](https://github.com/nostr-protocol/nips) | Identity, events, relays, and distribution all converge here. | Key management, relay ops, profile setup, posting, DM flows. | `Build now` |
| [NIP-47 / Nostr Wallet Connect](https://docs.nwc.dev/) | The cleanest agent surface in the stack. | Payment delegation, invoice creation, pay, balance, revoke. | `Build now` |
| [NIP-46 / Nostr Connect](https://github.com/nostr-protocol/nips) | Safer remote signing for Nostr operations. | Signer delegation and constrained signing policies. | `Build soon` |
| [NIP-57 zaps](https://github.com/nostr-protocol/nips) | Social Lightning UX that already works in production. | Zap setup, creator workflows, wallet wiring. | `Build soon` |
| [NIP-60 / NIP-61](https://github.com/nostr-protocol/nips) | Cashu wallet events and Nutzaps point to Nostr-native money flows. | Ecash sync, mint recommendations, Nutzap send/receive. | `Watch closely` |
| [Damus](https://damus.io/), [Primal](https://primal.net/join/), [Amethyst](https://github.com/vitorpamplona/amethyst) | These are the real user surfaces. | Onboarding, key safety, wallet hookup, relay management. | `Build soon` |

## 3. Private Comms and Resilient Publishing

### High-priority adjacent tools

| Product | Why it matters | Fit with Freedom Skills | Priority |
| --- | --- | --- | --- |
| [Signal](https://signal.org/blog/phone-number-privacy-usernames/) | Still the most usable secure messenger for normal people. | Important baseline and already skillable via `signal-cli`. | `Build now` |
| [SimpleX](https://github.com/simplex-chat/simplex-chat) | Strong metadata-minimizing modern messenger. | Very good bot and CLI surface; strong activist fit. | `Build now` |
| [Matrix](https://matrix.org/) / [Element](https://element.io/) | Best open ecosystem for communities, bots, and bridges. | Excellent automation fit for rooms, moderation, bridges, and ops. | `Build now` |
| [Delta Chat](https://delta.chat/) | Strong “meet people where they are” comms layer. | Good for email-native communities, bots, and mini-apps. | `Build soon` |
| [White Noise](https://www.whitenoise.chat/) | Private messaging on open protocols already close to Nostr. | Strong watchlist item for private comms inside the Bitcoin/Nostr orbit. | `Build soon` |
| [Nowhere](https://hostednowhere.com/) | Censorship-resistant sites encoded into URLs, with Nostr rails for live features. | Better fit for resilient publishing, stores, petitions, and drops than for everyday chat. | `Watch closely` |

### Specialist or watchlist tools

| Product | Why it matters | Freedom Skills judgment | Priority |
| --- | --- | --- | --- |
| [Bitchat](https://github.com/permissionlesstech/bitchat) | Offline Bluetooth mesh plus Nostr-based internet reach. | Strong protest/disaster story, but still app-centric and security-sensitive. | `Watch closely` |
| [Keet](https://keet.io/) | Philosophically aligned P2P comms. | Useful reference, but weaker Bitcoin/Nostr tie than White Noise or Bitchat. | `Watchlist` |
| [Session](https://getsession.org/) | Anonymity-oriented messaging. | Buildable enough to experiment with, but lower priority than Signal/SimpleX/Matrix. | `Watchlist` |
| [Briar](https://briarproject.org/) | Strong internet-shutdown and Android activist fit. | Mission fit is high, but automation surface looks weak today. | `Watchlist` |
| [Cwtch](https://cwtch.im/) | Metadata-conscious niche messenger. | Interesting, but niche and not a first-wave product target. | `Watchlist` |
| [Jami](https://jami.net/) | Long-running P2P comms project. | Worth understanding, not worth prioritizing for skills first. | `Watchlist` |
| [Meshtastic](https://meshtastic.org/) | Real offline/disaster communications layer. | Strong adjacent fit for activists and community operations. | `Build soon` |
| [Ceno](https://censorship.no/), [Tor](https://www.torproject.org/), [Psiphon](https://psiphon.ca/) | Critical anti-censorship access stack. | Important context for resilient publishing and distribution skills. | `Build soon` |

## 4. Supporting Sovereignty Infrastructure

| Tooling | Why it matters | Judgment |
| --- | --- | --- |
| [GPG / OpenPGP](https://gnupg.org/index.en.html) | Signed releases, operator comms, software provenance, archive integrity. | Yes, this should become a candidate Freedom Skill. |
| RSA-based tooling | Legacy crypto primitive still present in real systems. | Not a standalone skill. Fold it into `gpg-openpgp` or tightly-scoped OpenSSL operations. |
| [mesh-llm](https://github.com/Mesh-LLM/mesh-llm) | Sovereign/shared compute for agents with an OpenAI-compatible API. | Useful support infrastructure for Freedom Skills, not a core product track. |
| [Crabbox](https://github.com/openclaw/crabbox) | Agent-friendly ephemeral compute and test boxes. | Useful support infrastructure, not freedom tech itself. |

## 5. Recommended Build Order

### First wave

1. `nostr-ops`
2. `nwc-wallet`
3. `btcpay-greenfield`
4. `bitcoin-core-readonly`
5. `lnd-ops`
6. `core-lightning-ops`
7. `cashu-cli`
8. `fedimint-client`
9. `signal-cli`
10. `simplex-bot`
11. `matrix-community-ops`

### Second wave

1. `lnbits`
2. `zeus-helper`
3. `phoenix-support`
4. `gpg-openpgp`
5. `boltz-swaps`
6. `white-noise-core`
7. `meshtastic-ops`

### Watchlist

1. `nowhere`
2. `bitchat`
3. `keet`
4. `session`
5. `briar`
6. `mesh-llm`
7. `crabbox`

## 6. Bottom Line

If Freedom Skills wants a sharp thesis, it should stay centered on:

- sovereign Bitcoin operations
- programmable Lightning and wallet-connect flows
- ecash and federated money
- Nostr as the social, identity, and payments coordination layer
- practical private communications and resilient publishing that complement that stack

That keeps the project coherent. It also prevents the roadmap from drifting into “all privacy tools everywhere” instead of building the highest-leverage skills first.
