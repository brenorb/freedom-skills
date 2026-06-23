---
name: mdk-mcp
description: Connect coding agents to the Money Dev Kit MCP server. Use when Codex needs to install or explain the public signup MCP, authenticated account MCP, Cursor or VS Code deep links, Claude Code or Codex MCP commands, or when a Money Dev Kit workflow should use live MCP tools for account, app, product, customer, checkout, or docs operations.
---

# MDK MCP

Skill version: 0.1.0
Last reviewed against Money Dev Kit docs: 2026-04-27
Canonical docs: https://docs.moneydevkit.com/nextjs.md
Docs index fallback: https://docs.moneydevkit.com/llms.txt
Related services: https://mcp.moneydevkit.com/mcp/, https://mcp.moneydevkit.com/mcp/account/

## Workflow

Use this skill when an agent should connect to Money Dev Kit through MCP instead of relying only on static docs.

1. Decide which MCP endpoint is needed:
   - New account flow: `https://mcp.moneydevkit.com/mcp/`
   - Existing authenticated account flow: `https://mcp.moneydevkit.com/mcp/account/`
2. Install the endpoint in the user's agent environment.
3. For new account flows, ask for the user's real email and name before account creation.
4. For existing account flows, have the agent authenticate through the supported client flow.
5. Use MCP docs search/resources before implementing checkout or L402 code.
6. Use MCP tools to create or inspect Money Dev Kit account resources when available.
7. Store returned `MDK_ACCESS_TOKEN` and `MDK_MNEMONIC` as server-side environment variables only.

## Required Pattern

Read `references/mcp-install.md` before giving install commands. If install commands appear stale, check the canonical docs and docs index before answering.

## Guardrails

- Use the authenticated MCP endpoint for users who already have a Money Dev Kit account.
- Use the public MCP endpoint when the agent should create a new account.
- Do not print, log, or commit credentials returned by MCP.
- Use MCP as the live source for account operations; use docs as the source for code patterns.
