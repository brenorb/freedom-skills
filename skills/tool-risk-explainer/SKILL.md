---
name: tool-risk-explainer
description: Explain a freedom-tech tool's privacy, custody, availability, metadata, operator, and failure tradeoffs in plain language for a concrete use case.
---

# Tool Risk Explainer

Explain why a tool fits or fails a situation without marketing it or rejecting
it by label alone.

## Workflow

1. Identify the user's goal, adversary, data, urgency, technical ability, and
   acceptable failure or recovery cost.
2. Describe the tool's data flow, identifiers, operators, trust/custody,
   network dependencies, logs, recovery, and external side effects.
3. Compare the tool with one viable alternative and name the decision that
   changes the recommendation.
4. State what it protects, what it does not protect, common user mistakes, and
   a safer first test.
5. Give a stop condition and migration/exit path; cite current primary sources
   when product behavior may change.

Do not use “private,” “decentralized,” or “open source” as complete risk
assessments.

## Minimal check

The explanation names at least one trust assumption, one metadata exposure, one
failure mode, and one recovery path.
