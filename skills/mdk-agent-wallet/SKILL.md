---
name: mdk-agent-wallet
description: Use the Money Dev Kit agent wallet CLI for AI-agent Lightning payments. Use when Codex needs to initialize an agent wallet, receive or send Lightning payments, inspect wallet balance or payment history, pay L402 endpoints, parse JSON CLI output, or troubleshoot @moneydevkit/agent-wallet daemon behavior.
---

# MDK Agent Wallet

Skill version: 0.1.0
Last reviewed against Money Dev Kit docs: 2026-04-27
Canonical docs: https://docs.moneydevkit.com/agent-wallet.md
Docs index fallback: https://docs.moneydevkit.com/llms.txt
Related packages: @moneydevkit/agent-wallet

## Workflow

Use this skill when an AI agent needs a self-custodial Lightning wallet with JSON command output.

1. Check whether a wallet already exists with `npx @moneydevkit/agent-wallet@latest status` or `init --show`.
2. Initialize only when needed: `npx @moneydevkit/agent-wallet@latest init`.
3. Treat the mnemonic as secret. Do not print it unless the user explicitly requests backup instructions.
4. Use `receive <amount>` for inbound invoices, `send <destination> [amount]` for outbound payments, and `balance` for funds checks.
5. Parse stdout as JSON and rely on exit code `0` for success and `1` for errors.
6. For L402 APIs, request the protected endpoint, pay the returned invoice with the wallet, then retry with the token and payment preimage.
7. Restart the daemon if commands hang or return no output.

## Required Pattern

Read `references/agent-wallet.md` before writing wallet automation or L402 client code. If CLI output or commands appear stale, check the canonical docs and docs index before implementing.

## Guardrails

- The wallet is separate from the Money Dev Kit platform account flow, but compatible with Money Dev Kit paid APIs.
- Wallet config is stored in `~/.mdk-wallet/config.json` unless environment overrides are used.
- `MDK_WALLET_MNEMONIC` and the config mnemonic control funds and must be protected.
- Do not delete or reinitialize wallet state unless the user explicitly asks and confirms they have backed up the mnemonic.
- Prefer `@latest` in command examples so agents pick up wallet fixes.
