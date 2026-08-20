---
name: skill-portability-bench
description: Test whether one skill remains usable across agent runtimes by comparing behavior, formatting, tools, permissions, and maintenance deltas.
---

# Skill Portability Bench

Find runtime assumptions before they become compatibility bugs.

## Workflow

1. Freeze the same skill version, task, fixtures, model class, tools, and
   authorization boundary for each target harness.
2. Run a representative task set and record pass rate, output contract,
   formatting, tool-call compatibility, clarification behavior, and safety
   decisions.
3. Classify failures as unsupported metadata, missing tool, prompt semantics,
   filesystem layout, permission model, or harness-specific behavior.
4. Measure adaptation size and maintenance cost; keep the portable core separate
   from optional runtime hints.
5. Re-run after every portability change and retain a compatibility matrix.

Do not weaken safety constraints to make a skill appear portable.

## Minimal check

The matrix contains one positive task and one expected incompatibility with a
documented reason.
