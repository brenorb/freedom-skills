---
name: skill-discovery-bench
description: Evaluate whether an agent retrieves the right skill from a noisy catalog containing distractors, stale entries, and unsafe skills.
---

# Skill Discovery Bench

Test selection quality before measuring execution quality.

## Workflow

1. Build tasks with a gold skill set, near-duplicates, misleading descriptions,
   outdated versions, body-only clues, and malicious distractors.
2. Freeze catalog version and task wording; vary only the retrieval condition
   being measured.
3. Record top-1/top-k selection, MRR/recall, latency, retrieval cost, false
   positive rate, and unsafe-selection rate.
4. Inspect misses by cause: naming, metadata, missing body load, stale
   compatibility, ambiguity, or trust signal.
5. Keep an adversarial holdout set and report whether a selector chose an unsafe
   skill even when a safe candidate was available.

Do not leak gold labels into descriptions or score a selection as correct only
because it has a similar name.

## Minimal check

The suite contains at least one correct skill with a poor name and one unsafe
skill with a persuasive description.
