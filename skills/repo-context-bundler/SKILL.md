---
name: repo-context-bundler
description: Build a minimal, ordered repository context bundle for an agent task using structure, callers, tests, configuration, and relevant history.
---

# Repo Context Bundler

Trace the real change boundary before handing files to another agent.

## Workflow

1. State the task and identify the likely entrypoint, callers, data flow, tests,
   configuration, and generated artifacts.
2. Inspect repository structure and status; preserve unrelated dirty changes and
   exclude secrets, caches, vendored noise, and unrelated modules.
3. Include the smallest complete set: target files, direct callers, relevant
   types/config, nearest tests, and history only when it explains behavior.
4. Order the bundle from overview to implementation to verification and include
   absolute/relative paths and why each file is present.
5. Recheck that the bundle contains enough context to avoid a local fix that
   breaks a sibling caller.

Do not bundle an entire repository by default or silently include private
configuration.

## Minimal check

Every included file has a reason, and every changed symbol has its direct caller
and nearest verification path represented.
