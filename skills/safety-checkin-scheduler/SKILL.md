---
name: safety-checkin-scheduler
description: Design a privacy-aware check-in schedule with expected windows, escalation contacts, verification, expiry, and minimal location data.
---

# Safety Check-in Scheduler

Create a check-in plan that helps people notice a problem without turning every
check-in into a location or relationship graph.

## Workflow

1. Define participants, expected check-in windows, safe channels, travel or
   activity context, escalation delay, and who is authorized to act.
2. Use coarse status and the least identifying data needed; separate welfare
   escalation from ordinary coordination.
3. Define verification phrase, alternate channel, contact order, false-alarm
   handling, and what happens when a contact is unreachable.
4. Test the schedule with synthetic or low-risk data, including time-zone,
   device, power, and network failure.
5. Set expiry, review, and deletion rules; revoke the plan when the activity or
   risk ends.

Do not use a check-in plan as a substitute for emergency services or expose a
person's live location by default.

## Minimal check

The plan has a trigger, verification step, escalation owner, stop/expiry rule,
and offline fallback.
