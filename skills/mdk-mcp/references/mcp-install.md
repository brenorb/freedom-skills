# MCP Install Reference

Use the canonical docs index at https://docs.moneydevkit.com/llms.txt if anything here looks stale.

## New Account Endpoint

Use this when the agent should create a Money Dev Kit account.

```bash
claude mcp add moneydevkit --transport http https://mcp.moneydevkit.com/mcp/
```

```bash
codex mcp add moneydevkit --url https://mcp.moneydevkit.com/mcp/
```

Cursor:

```text
cursor://anysphere.cursor-deeplink/mcp/install?name=moneydevkit&config=eyJ1cmwiOiJodHRwczovL21jcC5tb25leWRldmtpdC5jb20vbWNwLyJ9
```

VS Code:

```text
vscode://mcp/install?name=moneydevkit&config=%7B%22url%22%3A%22https%3A//mcp.moneydevkit.com/mcp/%22%7D
```

## Existing Account Endpoint

Use this when the user already has a Money Dev Kit account.

```bash
claude mcp add moneydevkit --transport http https://mcp.moneydevkit.com/mcp/account/
```

```bash
codex mcp add moneydevkit --url https://mcp.moneydevkit.com/mcp/account/
```

Cursor:

```text
cursor://anysphere.cursor-deeplink/mcp/install?name=moneydevkit&config=eyJ1cmwiOiJodHRwczovL21jcC5tb25leWRldmtpdC5jb20vbWNwL2FjY291bnQvIn0=
```

VS Code:

```text
vscode://mcp/install?name=moneydevkit&config=%7B%22url%22%3A%22https%3A//mcp.moneydevkit.com/mcp/account/%22%7D
```

## Replit Agent

New account:

```text
https://replit.com/integrations?mcp=eyJkaXNwbGF5TmFtZSI6Im1vbmV5ZGV2a2l0IiwiYmFzZVVybCI6Imh0dHBzOi8vbWNwLm1vbmV5ZGV2a2l0LmNvbS9tY3AifQ==
```

Existing account:

```text
https://replit.com/integrations?mcp=eyJkaXNwbGF5TmFtZSI6Im1vbmV5ZGV2a2l0IChhdXRoZW50aWNhdGVkKSIsImJhc2VVcmwiOiJodHRwczovL21jcC5tb25leWRldmtpdC5jb20vbWNwL2FjY291bnQifQ==
```
