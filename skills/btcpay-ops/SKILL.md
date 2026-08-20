---
name: btcpay-ops
description: Configure and operate BTCPay Server stores, invoices, webhooks, POS flows, and reconciliation with least-privilege API access.
---

# BTCPay Ops

Use BTCPay's Greenfield/API surface for a specific merchant workflow without
confusing invoice creation, payment confirmation, and settlement.

## Workflow

1. Identify server, store, currency, product/order source, settlement wallet,
   webhook endpoint, and required operator role.
2. Inspect store and invoice state read-only; use scoped API keys and avoid
   exposing tokens in commands, logs, or generated code.
3. For creation or configuration, preview price, currency, expiry, redirect,
   payment method, webhook target, and refund policy before applying changes.
4. Verify webhook signatures/idempotency and reconcile invoice state against
   BTCPay rather than trusting a browser redirect.
5. Record store configuration, backup/export path, and a rollback procedure for
   integrations and extensions.

Do not mark an order paid from an unverified callback or expose customer data
while debugging.

## Minimal check

An end-to-end test proves that the intended invoice state, webhook, and
reconciliation record agree.
