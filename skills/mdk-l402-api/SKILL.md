---
name: mdk-l402-api
description: Build paid APIs with Money Dev Kit L402 payments. Use when Codex needs to protect Next.js or Express API routes with withPayment, implement HTTP 402 Lightning payment flows, create agent-readable paid API documentation, test L402 clients, or pair paid API access with the Money Dev Kit agent wallet.
---

# MDK L402 API

Skill version: 0.1.0
Last reviewed against Money Dev Kit docs: 2026-04-27
Canonical docs: https://docs.moneydevkit.com/l402.md
Docs index fallback: https://docs.moneydevkit.com/llms.txt
Related packages: @moneydevkit/nextjs, @moneydevkit/replit, @moneydevkit/agent-wallet

## Workflow

Use this skill to turn an API route into a pay-per-call endpoint using the L402 protocol.

1. Inspect the framework and route style before editing.
2. Ensure Money Dev Kit checkout setup already exists or add the relevant `@moneydevkit/nextjs` or `@moneydevkit/replit` integration first.
3. Confirm `MDK_ACCESS_TOKEN` and `MDK_MNEMONIC` are present in server-side environment variables.
4. Wrap the target handler with `withPayment({ amount, currency, expirySeconds? }, handler)`.
5. Use `currency: "SAT"` for satoshi pricing or `currency: "USD"` for US cents.
6. For dynamic pricing, derive the amount deterministically from the request and keep it stable between invoice creation and token verification.
7. Document client behavior: first request receives 402 with invoice and token, client pays invoice, client retries with `Authorization: L402 <token>:<preimage>`.
8. If the API is intended for agents, add or update `llms.txt` with the endpoint, pricing, auth flow, and agent wallet payment instructions.
9. Test unauthenticated requests return 402 and valid paid requests reach the handler.

## Required Pattern

Read `references/l402-api.md` before editing files. Follow the examples there unless the canonical docs have changed.

If code examples or package APIs appear stale, check the canonical docs and the docs index before implementing. Prefer current docs over this bundled reference.

## Guardrails

- Do not invent a custom payment auth scheme when L402 fits.
- Do not expose Money Dev Kit secrets in client code or `llms.txt`.
- Preserve any existing route validation and authorization logic inside the paid handler.
- Return useful non-sensitive API docs so agents can discover how to pay and retry.
- Pair with `mdk-agent-wallet` when building clients that should pay L402 endpoints.
