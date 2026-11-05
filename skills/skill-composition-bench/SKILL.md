---
name: skill-composition-bench
description: Evaluate multi-skill workflows that require two or more skills in sequence, including ordering, handoff, redundancy, and context loss.
---

# Skill Composition Bench

Test the seams between skills, where otherwise-good instructions often fail.

## Workflow

1. Define a task requiring a minimal skill set, such as wallet review plus
   threat model, or archive plus evidence packaging.
2. Specify allowed orderings, handoff artifacts, stop/approval checkpoints,
   and the final verifier output.
3. Record task success, order correctness, extra skill loads, redundant calls,
   context loss, authorization drift, and recovery after a partial failure.
4. Compare the minimal composition with supersets and wrong-order controls.
5. Preserve the intermediate artifacts so a failure can be assigned to a skill,
   handoff, or harness rather than guessed.

Do not reward a composition for using more skills than the task requires.

## Minimal check

The suite includes one wrong-order control that produces a detectable failure or
warning.
