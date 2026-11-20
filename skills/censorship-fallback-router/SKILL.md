---
name: censorship-fallback-router
description: Choose an authorized alternate access or publication path when a domain, service, or network route is blocked, degraded, or unsafe.
---

# Censorship Fallback Router

Route around a failure while making exposure and trust changes explicit.

## Workflow

1. Identify whether the failure is DNS, domain, IP, protocol, account, local
   network, national filtering, or service outage; preserve the original URL.
2. Rank alternatives by urgency and risk: cached/offline copy, official mirror,
   alternate domain, archive, onion/IPFS, approved proxy/VPN/Tor, or physical
   transfer.
3. Check authenticity and freshness of the alternate before use; do not trust a
   mirror solely because it is reachable.
4. Explain metadata, account, legal, malware, and availability tradeoffs before
   enabling a new route or publishing through it.
5. Record the working path, verification evidence, expiry, and rollback; ask
   before changing network settings or sending content.

Do not promise censorship circumvention or anonymity, and do not defeat access
controls the user is not authorized to bypass.

## Minimal check

The selected fallback has both an authenticity check and a stop condition for a
route that becomes unsafe or unverified.
