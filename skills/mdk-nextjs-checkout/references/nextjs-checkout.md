# Next.js Checkout Reference

Use the canonical docs at https://docs.moneydevkit.com/nextjs.md if anything here looks stale.

## Install

```bash
npm install @moneydevkit/nextjs
```

Use the repo's package manager when it is not npm.

## Environment

```env
MDK_ACCESS_TOKEN=your_api_key_here
MDK_MNEMONIC=your_mnemonic_here
```

## Unified Route

```ts
// app/api/mdk/route.ts
export { POST } from "@moneydevkit/nextjs/server/route";
```

## Next Config

```ts
// next.config.ts
import withMdkCheckout from "@moneydevkit/nextjs/next-plugin";

export default withMdkCheckout({});
```

## Create Checkout

```tsx
"use client";

import { useCheckout } from "@moneydevkit/nextjs";
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
      metadata: { source: "nextjs-checkout" },
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
// app/checkout/[id]/page.tsx
"use client";

import { Checkout } from "@moneydevkit/nextjs";
import { use } from "react";

export default function CheckoutPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <Checkout id={id} />;
}
```

## Success Verification

```tsx
"use client";

import { useCheckoutSuccess } from "@moneydevkit/nextjs";

export default function SuccessPage() {
  const { isCheckoutPaidLoading, isCheckoutPaid, metadata } = useCheckoutSuccess();

  if (isCheckoutPaidLoading || isCheckoutPaid === null) return <p>Verifying payment...</p>;
  if (!isCheckoutPaid) return <p>Payment has not been confirmed.</p>;

  return <p>Payment confirmed for {metadata?.name ?? "customer"}.</p>;
}
```
