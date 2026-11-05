---
name: private-comms-setup
description: "Use this skill when helping a non-technical person choose and set up a safer communication tool. Focus on practical tradeoffs, simple recommendations, and configuration steps that materially improve privacy."
---

# Private Comms Setup

Help the person choose one practical tool and configure it safely. Keep the advice simple and honest.

## Default workflow

1. Ask four things first: who they need to talk to, what devices they use, whether sharing a phone number is acceptable, and what they are worried about.
2. Recommend one primary tool and at most one fallback. Do not dump a long comparison table unless asked.
3. Explain the tradeoff in plain language: convenience, contact reach, metadata exposure, backups, and recovery risk.
4. Walk through setup in order and call out the few settings that matter.
5. End with a short "use it this way" checklist for everyday habits.

## Default recommendations

- Prefer Signal for most people who can get their contacts to install one new app. It is usually the best privacy-to-usability default.
- Prefer SimpleX when phone-number privacy or contact-graph exposure matters more than convenience.
- Use WhatsApp only when the group will not move. Explain that message content protection is not the same as metadata privacy, and backups can weaken privacy if configured badly.
- Use iMessage only as a pragmatic Apple-only fallback, not as a universal recommendation.
- Move highly sensitive conversations out of plain SMS and ordinary email.

## Setup checklist

- Turn on the app's registration lock or equivalent account protection.
- Turn on screen lock for the app if available.
- Set disappearing messages for sensitive chats.
- Review backups explicitly. If backups are not end-to-end encrypted, prefer disabling them for sensitive use.
- Verify the contact identity for high-risk conversations using the app's built-in safety check.
- Keep the phone OS and app updated.

## Guardrails

- Do not promise anonymity, invisibility, or perfect safety.
- Say clearly when privacy depends on both sides using the same tool correctly.
- If the recommendation turns on an exact product feature, check the current official docs before giving step-by-step instructions.
- Prefer a tool the person will actually use correctly over a "better" tool they will abandon.
