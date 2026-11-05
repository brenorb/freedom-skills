---
name: skill-fit-bench
description: Measure whether loading a candidate skill improves task success enough to justify its context, latency, and risk cost.
---

# Skill Fit Bench

Measure the delta a skill creates against a no-skill baseline.

## Workflow

1. Define a task with a deterministic or human-reviewed success condition and
   run no-skill, correct-skill, and retrieved-skill conditions.
2. Keep model, harness, tools, permissions, task data, and retry policy fixed.
3. Record pass rate, partial success, cost, latency, context size, unnecessary
   skill loads, negative delta, and unsafe side effects.
4. Inspect whether the skill improved decisions, tool use, safety, or only added
   repeated prose; preserve failed artifacts for diagnosis.
5. Set a practical adoption threshold and test it on a held-out task family.

Do not call a skill useful because the agent mentioned it or because a single
expert preferred its wording.

## Minimal check

Every positive result is compared with a no-skill run from the same fixture and
has a recorded success criterion.
