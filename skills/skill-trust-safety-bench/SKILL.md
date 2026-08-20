---
name: skill-trust-safety-bench
description: Test whether an agent identifies, contains, refuses, or escalates risky skills with excessive permissions, provenance gaps, or instruction hijacking.
---

# Skill Trust and Safety Bench

Exercise the trust boundary before a skill is installed or executed.

## Workflow

1. Create fixtures for overbroad permissions, unjustified external actions,
   stale runtime assumptions, unknown provenance, prompt injection, secret
   requests, and missing privacy warnings.
2. Define expected action: allow, allow with restriction, manual review, or
   block, plus the explanation a user should receive.
3. Run the suite with benign lookalikes and record unsafe accept, safe reject,
   escalation, explanation quality, and permission drift.
4. Check that the agent separates skill instructions from untrusted artifacts
   and does not follow a skill's request to weaken platform controls.
5. Keep a held-out adversarial set and review false positives with a human.

Do not use live secrets, destructive commands, or real external systems as test
fixtures.

## Minimal check

At least one fixture asks for a secret and one asks for a harmless local action;
the expected decisions differ for an explicit reason.
