---
name: mdk-replit-checkout
description: Integrate Money Dev Kit checkout into Replit Vite, React, and Express applications. Use when Codex needs to add or repair @moneydevkit/replit setup, mount the Express /api/mdk route, add checkout UI, configure Replit bundler allowlists, or help Replit Agent implement Lightning checkout with Money Dev Kit.
---

# MDK Replit Checkout

Skill version: 0.1.0
Last reviewed against Money Dev Kit docs: 2026-04-27
Canonical docs: https://docs.moneydevkit.com/replit.md
Docs index fallback: https://docs.moneydevkit.com/llms.txt
Related packages: @moneydevkit/replit, express

## Workflow

Use this skill for Replit projects that use Vite + React on the client and Express on the server.

1. Confirm the project has both client and server runtimes. Do not use this for static design-only Replit projects.
2. Inspect package manager, server entrypoint, Vite client entrypoint, routing conventions, and `script/build.ts`.
3. Ask for the user's email and name before creating a Money Dev Kit account through MCP.
4. Install `@moneydevkit/replit` and `express` when needed.
5. Add `MDK_ACCESS_TOKEN` and `MDK_MNEMONIC` to Replit environment variables. Do not hard-code them.
6. Add `@moneydevkit/core` and `@moneydevkit/replit` to the Replit bundler allowlist when `script/build.ts` exists.
7. Mount `createMdkExpressRouter()` at `/api/mdk`.
8. Add a client checkout trigger with `useCheckout()`.
9. Add a checkout route with `<Checkout id={id} />`.
10. Verify payment success with `useCheckoutSuccess()` if the app has a success page.
11. Restart the Replit app after package installation and route changes.

## Required Pattern

Read `references/replit-checkout.md` before editing files. Follow the examples there unless the canonical docs have changed.

If code examples or package APIs appear stale, check the canonical docs and the docs index before implementing. Prefer current docs over this bundled reference.

## Guardrails

- Use `@moneydevkit/replit`, not `@moneydevkit/nextjs`.
- Sandbox payments should work in the Replit preview window without a wallet.
- Both `MDK_ACCESS_TOKEN` and `MDK_MNEMONIC` are required.
- Keep the client pointed at `/api/mdk`; the Express route handles Money Dev Kit server work.
- Use the app URL when creating an app through MCP so callbacks and sandbox behavior match the Replit deployment.
