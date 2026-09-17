---
name: session-orchestrator
description: Plan resumable handoffs between agent sessions with durable state, explicit ownership, checkpoints, and least-privilege continuation.
---

# Session Orchestrator

Make a long task resumable without pretending conversation history is a
reliable database.

## Workflow

1. Define objective, owner, deadline, permissions, external side effects, and
   the next safe checkpoint.
2. Write a compact state record with done, in-progress, blocked, decisions,
   artifacts, branch/worktree, tests, and exact next action.
3. When handing off, include only relevant files and secrets-free context;
   distinguish observations from assumptions and stale plans.
4. On resume, verify repository state, external state, branch, and approvals
   before repeating or mutating anything.
5. Close the session by updating the state record and naming unresolved risk or
   a human decision required.

Do not duplicate external sends or financial actions because a checkpoint is
ambiguous.

## Minimal check

The next session can determine what not to repeat from the durable state file
alone.
