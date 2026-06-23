# L402 API Reference

Use the canonical docs at https://docs.moneydevkit.com/l402.md if anything here looks stale.

## Next.js Route

```ts
// app/api/premium/route.ts
import { withPayment } from "@moneydevkit/nextjs/server";

const handler = async (req: Request) => {
  return Response.json({ content: "Premium data" });
};

export const GET = withPayment(
  { amount: 100, currency: "SAT" },
  handler,
);
```

## Express Route

```ts
import { withPayment } from "@moneydevkit/replit/server/express";

const handler = async (req: Request) => {
  return Response.json({ content: "Premium data" });
};

app.get("/api/premium", withPayment(
  { amount: 100, currency: "SAT" },
  handler,
));
```

## Dynamic Pricing

```ts
export const POST = withPayment(
  {
    amount: (req: Request) => {
      const url = new URL(req.url);
      return url.searchParams.get("tier") === "pro" ? 500 : 100;
    },
    currency: "SAT",
  },
  handler,
);
```

The pricing function is evaluated during invoice creation and verification. Keep it deterministic.

## Client Flow

```bash
curl -s https://example.com/api/premium
```

The first response should be HTTP 402 with an invoice and token.

```bash
curl -s https://example.com/api/premium \
  -H "Authorization: L402 <token>:<preimage>"
```

## Agent-Readable Docs

When the API is meant for agents, add an `llms.txt` entry that includes:

- Endpoint URL and method.
- JSON request and response examples.
- Price in sats or US cents.
- Statement that unauthenticated requests return HTTP 402.
- Instruction to pay the returned Lightning invoice and retry with `Authorization: L402 <token>:<preimage>`.
- Agent wallet command examples when applicable.
