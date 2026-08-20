---
name: privacy-payment-advisor
description: Compare Bitcoin, Lightning, Cashu, Fedimint, Liquid, CoinJoin, PayJoin, and related payment paths against a concrete privacy and operational need.
---

# Privacy Payment Advisor

Choose a payment rail by threat model and failure tolerance, not by a generic
claim that one rail is “private.”

## Workflow

1. Ask for amount range, recipient relationship, timing, repeat pattern,
   custody, recovery, fees, offline needs, and who must not learn what.
2. Compare candidate rails on observer visibility, linkability, trust/custody,
   liquidity, reversibility, fees, availability, and user error.
3. Explain the full lifecycle: acquire, receive, spend, change/refund, backup,
   and exit. Flag metadata outside the payment protocol.
4. Recommend the least risky workable option and a small test; state what the
   recommendation does not protect against.
5. Avoid giving legal, tax, or evasion advice as if it were a protocol fact.

Do not select or execute a payment without a clear destination and current
authorization.

## Minimal check

The advice names the observer model, trust assumption, and recovery failure for
the recommended rail.
