---
name: mdk-nextjs-checkout
description: Integrate Money Dev Kit checkout into Next.js App Router projects. Use when Codex needs to add or repair @moneydevkit/nextjs setup, create checkout flows, expose the /api/mdk route, configure the Next.js plugin, verify checkout success pages, or help an app accept Lightning payments with Money Dev Kit.
---

# MDK Next.js Checkout

Skill version: 0.1.0
Last reviewed against Money Dev Kit docs: 2026-04-27
Canonical docs: https://docs.moneydevkit.com/nextjs.md
Docs index fallback: https://docs.moneydevkit.com/llms.txt
Related packages: @moneydevkit/nextjs, @moneydevkit/create

## Workflow

Use this skill to add a full Money Dev Kit checkout loop to a Next.js App Router application.

1. Inspect the app structure first: package manager, Next.js version, `app/` location, TypeScript usage, existing checkout/payment routes, and current environment variable handling.
2. If the project can use MCP tools, prefer the Money Dev Kit MCP for account/app creation. Otherwise tell the user to create an account at https://moneydevkit.com or run `npx @moneydevkit/create`.
3. Install `@moneydevkit/nextjs`.
4. Add `MDK_ACCESS_TOKEN` and `MDK_MNEMONIC` to server-side environment variables. Never commit these values.
5. Add the unified route at `app/api/mdk/route.ts` or `.js`.
6. Wrap Next config with `@moneydevkit/nextjs/next-plugin`.
7. Add a client checkout trigger with `useCheckout()`.
8. Add a checkout page using `<Checkout id={id} />`.
9. Add success verification with `useCheckoutSuccess()` when the app needs fulfillment or confirmation UI.
10. Run the app's existing typecheck, lint, or build checks.

## Required Pattern

Read `references/nextjs-checkout.md` before editing files. Follow the examples there unless the canonical docs have changed.

If code examples or package APIs appear stale, check the canonical docs and the docs index before implementing. Prefer current docs over this bundled reference.

## Guardrails

- Use App Router patterns. Do not implement this skill as a Pages Router integration unless the user explicitly asks for legacy support.
- Keep secrets on the server only.
- Use `currency: "USD"` for cents and `currency: "SAT"` for satoshis.
- Preserve existing app routing, styling, and package manager conventions.
- For product checkouts, use product IDs from Money Dev Kit instead of hard-coded amount fields.
