---
name: prompt-packager
description: Assemble a compact, harness-specific task packet from a user's goal, constraints, relevant files, and required output checks.
---

# Prompt Packager

Package context so an agent can act without dragging irrelevant private data
into the task.

## Workflow

1. Extract objective, done condition, constraints, authorization boundaries,
   environment, and expected output.
2. Select the smallest relevant file set; summarize large files with paths and
   line anchors instead of copying everything.
3. Separate instructions, facts, untrusted artifacts, secrets, and examples;
   never include credentials merely because they are nearby.
4. Adapt command and output format to the target harness while preserving the
   same user intent and stop conditions.
5. Add a validation checklist and an explicit question only for information
   that materially changes the action.

Do not weaken permissions or convert a read-only request into an execution
request during packaging.

## Minimal check

The packet can be understood without opening unrelated files and states exactly
what success will be verified against.
