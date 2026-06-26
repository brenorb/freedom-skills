# Agent Wallet Reference

Use the canonical docs at https://docs.moneydevkit.com/agent-wallet.md if anything here looks stale.

## Commands

```bash
npx @moneydevkit/agent-wallet@latest init
```

```bash
npx @moneydevkit/agent-wallet@latest balance
```

```bash
npx @moneydevkit/agent-wallet@latest receive 1000
```

```bash
npx @moneydevkit/agent-wallet@latest send user@example.com 500
```

```bash
npx @moneydevkit/agent-wallet@latest payments
```

```bash
npx @moneydevkit/agent-wallet@latest restart
```

## JSON Output Examples

```json
{"balance_sats":50000}
```

```json
{"invoice":"lnbc10n1...","payment_hash":"abc123...","expires_at":"2024-01-15T12:00:00.000Z"}
```

```json
{"payment_hash":"def456..."}
```

## Supported Send Destinations

- BOLT11 invoices: `lnbc...`, `lntb...`, `lntbs...`
- BOLT12 offers: `lno...`
- LNURL: `lnurl...`
- Lightning addresses: `user@domain.com`

## Config

The default config path is `~/.mdk-wallet/config.json`.

Environment overrides:

```env
MDK_WALLET_MNEMONIC=word word word ...
MDK_WALLET_PORT=3456
```

## L402 Client Pattern

1. Request the paid endpoint without credentials.
2. Parse the HTTP 402 response for invoice and token.
3. Pay the invoice with `agent-wallet send <invoice>`.
4. Extract the payment preimage from wallet output when available.
5. Retry the endpoint with `Authorization: L402 <token>:<preimage>`.
