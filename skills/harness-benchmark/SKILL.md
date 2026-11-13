---
name: harness-benchmark
description: Compare agent harnesses on the same task set with fixed prompts, tools, models, verifiers, cost, latency, and failure labels.
---

# Harness Benchmark

Measure harness behavior, not anecdotal preference.

## Workflow

1. Freeze task prompts, repository state, model/version, permissions, tools,
   timeout, temperature, and starting context for every harness.
2. Run the same tasks under the same authorization boundary with isolated
   workspaces and deterministic fixtures where possible.
3. Score artifact correctness, verifier result, tool errors, clarification
   turns, latency, tokens/cost, unsafe actions, and reproducibility.
4. Report per-task results and confidence intervals; separate harness failures,
   model failures, environment failures, and task ambiguity.
5. Publish the runner configuration and raw result hashes so another operator
   can reproduce the comparison.

Do not rank harnesses from one task or silently give one harness extra context
or permissions.

## Minimal check

Re-running one fixed task from a clean workspace produces the same verifier
inputs and explains any output difference.
