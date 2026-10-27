---
name: napplet-interop
description: Use only when a napplet talks to other napplets - NAP-INC topics (inc.emit / inc.on), NAP-INTENT dispatch (intent.invoke / intent.open), archetype manifest metadata, and the stable queryless convention identity rule (napplet:<archetype>/<intent>). Covers the emit-only query shorthand, payload validation, and what must stay exact-match. Skip for napplets that never emit, subscribe, or dispatch.
compatibility: CLI workflows assume `@napplet/cli` 0.13.0; package versions are independent, so verify installed SDK types.
license: MIT
metadata:
  version: "0.2.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
  upstream_sha: "6c4dafd20142cade5a51ae049beecfef7c8f7c2e"
  upstream_cli: "0.13.0"
  upstream_sdk: "0.30.0"
  upstream_source: "https://github.com/napplet/web/tree/6c4dafd20142cade5a51ae049beecfef7c8f7c2e/skills/napplet-interop"
---

# Inter-Napplet Conventions (INC, INTENT, archetypes)

Load this only when the design spec names a cross-napplet feature: opening a note/profile/DM in another napplet, exposing an archetype role, broadcasting to sibling napplets. Protocol truth is the living [NAP-INC](https://github.com/napplet/naps/blob/master/naps/NAP-INC.md) (draft history in [PR #89](https://github.com/napplet/naps/pull/89)) and [NAP-INTENT](https://github.com/napplet/naps/blob/master/naps/NAP-INTENT.md) documents. If a needed behavior is not there, flag the gap; do not invent it.

## Convention identity

One convention is one stable, **queryless** string: `napplet:<archetype>/<intent>`, e.g. `napplet:note/open`, `napplet:profile/open`, `napplet:dm/open`. It is an identifier, not a payload schema and not a version.

- Subscriptions, manifest discovery, and handler routing use **exact** matching on that identity. No query parsing, prefix, wildcard, canonicalization, payload-schema, or multi-convention matching anywhere in those paths.
- Never put query text in manifest metadata or in a subscription topic.
- Payload shape is a local choice per convention. Every received payload is untrusted: validate it against the real upstream convention when one exists; never infer a schema from the topic name and never recreate numbered payload contracts.

## Archetype metadata (manifest)

A napplet that fulfils an archetype role advertises one contract per entry through the vite-plugin `archetypes` option, which the CLI's `napplet init --archetype napplet:<archetype>/<intent>` also records in `.napplet/config.yaml`:

```ts
archetypes: [{ slug: 'note', convention: 'napplet:note/open' }],
```

This emits the manifest tag `["z", "note"]` and `["i", "napplet:note/open"]`. The convention's archetype segment matches a `z` role on the same manifest for dispatch eligibility; trailing `i` values advertise parameter names. Do not add payload, version, or negotiation fields.

## NAP-INC — broadcast between napplets

```ts
import { inc } from '@napplet/sdk';

inc.emit('napplet:profile/open', { pubkey: 'abc123' });

const sub = inc.on('napplet:profile/open', (event) => {
  if (!isValidProfileOpenPayload(event.payload)) return;   // untrusted input
  openProfile(event.payload);
});
sub.close();
```

`inc.on` delivers one `IncEvent` with the exact topic, a runtime-attested sender, and an optional payload.

### Emit-only query shorthand

Outbound `inc.emit(topic, payload?)` may take a queried convention URI as developer shorthand:

```ts
inc.emit('napplet:profile/open?pubkey=abc123');
// runtime sends { type: 'inc.emit', topic: 'napplet:profile/open', payload: { pubkey: 'abc123' } }
```

The runtime percent-decodes the shallow text query into the payload (`+` stays a literal plus) and routes the **queryless** topic, which subscribers match exactly. This is outbound preprocessing only, not a routing rule. These throw synchronously: a fragment, malformed percent encoding, a repeated decoded name, and a query combined with an explicit payload. For structured or non-text data use a queryless topic plus an explicit payload object.

The deprecated `ifc` SDK subpath is only an INC compatibility alias; new code imports `inc`.

## NAP-INTENT — ask the shell to route an action

```ts
import { intent } from '@napplet/sdk';

const accepted = await intent.open('napplet:profile/open', {
  payload: { pubkey: 'abc123' },
  behavior: { reuse: false },
});
if (!accepted.ok) showIntentError(accepted.error);
// accepted.ok means the runtime accepted the request, not that delivery finished.

const delivery = intent.onDelivery(({ payload }) => {
  if (isProfilePayload(payload)) renderProfile(payload.pubkey);
});
// Close `delivery` when the target view is disposed.
```

- Dispatch with `intent.invoke(uri, options?)` or the `intent.open(uri, options?)` convenience.
- Dispatch requests use a full URI such as `napplet:profile/open`; pass data in `payload` and runtime hints such as `behavior.reuse` separately.
- The caller's `ok` field reports acceptance; delivery is a separate target-side `intent.onDelivery` subscription. Targets validate the delivered payload before use. Do not treat acceptance as delivery confirmation.
- The URI derives archetype and action; target delivery is independent of INC and source lifetime.

## Spec lines to fill in

Add these to the `napplet-design` spec when interop is in scope:

```
archetype metadata: <none | slug + napplet:<archetype>/<intent>>
INC topics: <none | exact topic(s) emitted / subscribed + payload validation source>
intent dispatch: <none | invoke/open request + how acceptance and onDelivery drive the UI>
```

## Pitfalls

- Subscribing to a queried topic (`inc.on('napplet:profile/open?pubkey=…')`) — never matches; subscribe to the queryless identity.
- Treating a topic as a schema (`if (topic.endsWith('/open')) payload.pubkey…`) — validate the payload itself.
- Adding `inc` or `intent` to manifest `requires` for an optional handoff — gate on `window.napplet?.inc` / `?.intent` and hide the affordance when absent.
- Inventing delivery identifiers, acknowledgement lifecycles, or version negotiation around intents — not in the living spec; use the acceptance result and onDelivery contract.
