---
name: wallet-comparator
description: "Use this skill when the user wants to choose or compare Bitcoin wallets by custody, privacy, Lightning support, hardware wallet support, and the user's actual profile such as beginner saver, mobile spender, privacy-focused user, or advanced self-custody operator."
---

# wallet-comparator

Compare wallets for the user's situation, not as a generic top-10 list.

## Default workflow

1. Lock the decision frame first: funds at risk, device, on-chain or Lightning, hardware requirement, privacy priority, and user profile.
2. If the user did not name candidates, pick 3 to 5 wallets that cover the real tradeoffs. Do not compare near-duplicates.
3. Return a compact table with these columns: wallet, custody, privacy, Lightning, hardware, best for, main tradeoff.
4. Rank the options and end with one clear default recommendation plus one backup for a different priority such as easier setup or stronger privacy.
5. If the user is early-stage, include the upgrade path: what they can start with now and when they should move to a hardware-backed setup.

## Defaults

- Prefer comparisons by user profile: beginner saver, daily spender, Lightning-heavy user, privacy-first user, and advanced self-custody user.
- Separate spending wallets from savings wallets. A good wallet for coffee money is often the wrong wallet for long-term storage.
- Treat custody as the first branch: custodial, self-custodial, or collaborative/multisig.
- Treat hardware support as mandatory for meaningful savings, not a nice-to-have.
- Be blunt about tradeoffs. Better privacy usually costs convenience. Better Lightning UX may cost custody or recovery simplicity.

## Red flags

- Do not recommend a custodial wallet for long-term savings without saying exactly what the user gives up.
- Do not imply that "supports Lightning" means the same thing across custodial, on-device, and node-backed designs.
- Do not flatten privacy into a single score. Call out KYC exposure, metadata leakage, and network privacy separately when they matter.
