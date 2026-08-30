---
name: harness-chooser
description: "Use this skill when the user asks which agent or harness should handle a task, or when you need to route work between chat-only help, local coding agents, browser-capable agents, or research-heavy systems based on the task, risk, and the user's technical profile."
---

# harness-chooser

Choose the harness that matches the job, not the one with the most features.

## Default workflow

1. Classify the task first: chat/advice, local code edits, repo-wide refactor, browser automation, long-running research, or high-risk external action.
2. Classify the user next: non-technical, technical but busy, power user, or operator who wants reproducible terminal steps.
3. Recommend one primary harness and one fallback. Explain the choice in terms of access, speed, autonomy, and risk.
4. Spell out the handoff boundary: what the harness can do directly, what still needs confirmation, and what artifacts it should return.
5. If the task mixes modes, split it: research in one harness, implementation in another, and final review in the most reliable one.

## Defaults

- Prefer the simplest harness that has the needed access.
- Prefer local coding harnesses for repo edits, tests, and file-aware refactors.
- Prefer browser-capable harnesses only when the task truly depends on web UI state, login sessions, or visual verification.
- Prefer chat-only agents for framing, outlining, and prompt cleanup, not for repo-specific decisions without file access.
- Prefer conservative, confirmation-heavy harnesses for public posts, money movement, or secret handling.

## Routing heuristics

- Need code changes plus tests: pick a local coding harness.
- Need current web facts or live product comparison: pick a browsing harness.
- Need logged-in site actions or UI debugging: pick a browser-control harness.
- Need fast ideation or request cleanup for a novice user: pick a chat-first harness.
- Need multi-step work with side effects: pick the harness with the clearest confirmation boundary, even if it is slower.

## Red flags

- Do not recommend a browser harness for tasks that are easier and safer in the terminal.
- Do not recommend a chat-only harness for repo-specific implementation decisions without file access.
- Do not equate "best model" with "best harness". Access and tool fit matter more than raw model quality.
