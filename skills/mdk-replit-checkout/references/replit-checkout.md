# Replit Checkout Reference

Use the canonical docs at https://docs.moneydevkit.com/replit.md if anything here looks stale.

## Install

```bash
npm install @moneydevkit/replit express
```

Use the repo's package manager when it is not npm.

## Environment

```env
MDK_ACCESS_TOKEN=your_api_key_here
MDK_MNEMONIC=your_mnemonic_here
```

## Replit Bundler Allowlist

```ts
// script/build.ts
const allowlist = [
  "@moneydevkit/core",
  "@moneydevkit/replit",
];
```

Merge these entries into an existing allowlist instead of replacing unrelated packages.

## Express Route

```ts
import express from "express";
import { createMdkExpressRouter } from "@moneydevkit/replit/server/express";

const app = express();
app.use("/api/mdk", createMdkExpressRouter());
```

## Create Checkout

```tsx
import { useCheckout } from "@moneydevkit/replit";
import { useState } from "react";

export function BuyButton() {
  const { createCheckout, isLoading } = useCheckout();
  const [error, setError] = useState<string | null>(null);

  async function handlePurchase() {
    setError(null);
    const result = await createCheckout({
      type: "AMOUNT",
      title: "Purchase title",
      description: "Purchase description",
      amount: 500,
      currency: "USD",
      successUrl: "/checkout/success",
      metadata: { source: "replit-checkout" },
    });

    if (result.error) {
      setError(result.error.message);
      return;
    }

    window.location.href = result.data.checkoutUrl;
  }

  return (
    <>
      {error ? <p>{error}</p> : null}
      <button onClick={handlePurchase} disabled={isLoading}>
        {isLoading ? "Creating checkout..." : "Buy now"}
      </button>
    </>
  );
}
```

## Checkout Page

```tsx
import { Checkout } from "@moneydevkit/replit";

export default function CheckoutPage({ params }: { params: { id: string } }) {
  return <Checkout id={params.id} />;
}
```

## Success Verification

```tsx
import { useCheckoutSuccess } from "@moneydevkit/replit";

export function SuccessPage() {
  const { isCheckoutPaidLoading, isCheckoutPaid, metadata } = useCheckoutSuccess();

  if (isCheckoutPaidLoading || isCheckoutPaid === null) return <p>Verifying payment...</p>;
  if (!isCheckoutPaid) return <p>Payment has not been confirmed.</p>;

  return <p>Payment confirmed for {metadata?.name ?? "customer"}.</p>;
}
```
