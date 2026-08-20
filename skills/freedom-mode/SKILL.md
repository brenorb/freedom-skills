---
name: freedom-mode
description: Design a resilient operating plan for censorship, outages, or infrastructure failure using layered communications, cached information, and offline fallbacks.
---

# Freedom Mode

Build a human-readable fallback plan; do not silently change a user's network,
identity, or communications.

## Workflow

1. Identify the failure: blocked domain, DNS failure, internet outage, mobile
   overload, power loss, device loss, or unsafe operating environment.
2. Rank the user's needs by urgency: emergency contact, coordination,
   information access, publishing, payments, or recovery.
3. Choose the least risky working layer first: cached/offline material,
   ordinary network, approved proxy/VPN/Tor path, SMS/voice, local Wi-Fi, or
   mesh/physical transfer.
4. Define what is prepared before failure: contact cards, offline maps,
   verified installers, spare power, recovery codes, and printed instructions.
5. Write explicit switch and stop conditions. Ask before sending messages,
   enabling a proxy, publishing content, or exposing a location.

Avoid promising that any transport is anonymous or available. Treat every
fallback as a new metadata and trust boundary.

## Minimal check

The final plan must contain one offline path, one human decision checkpoint,
and one recovery path back to normal operation.
