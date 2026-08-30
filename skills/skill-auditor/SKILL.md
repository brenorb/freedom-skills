---
name: skill-auditor
description: "Use this skill before installing, adopting, or publishing a skill when you need a fast risk review focused on external actions, secret handling, scope creep, destructive behavior, and weak confirmation boundaries."
---

# Skill Auditor

Review the skill before anyone installs or relies on it. Prioritize risk, not style.

## Default workflow

1. Read the target `SKILL.md` fully.
2. Read every file the skill tells the agent to load, run, or trust: `references/`, `scripts/`, templates, manifests, and app metadata.
3. Mark every external action, state-changing action, secret touchpoint, and destructive command.
4. Check whether the skill makes the safe path the default path.
5. Report findings in severity order, then give a ship recommendation: `approve`, `approve with fixes`, or `do not install`.

## What to look for

- External effects without an explicit confirmation step.
- Destructive commands, account changes, posting, messaging, purchases, or network writes framed as routine.
- Secret exposure through shell history, logs, screenshots, pasted tokens, or unsafe CLI flags.
- Overbroad instructions such as "always" or "just do it" where the correct action depends on context.
- Hidden setup costs: obscure dependencies, interactive flows, fragile auth, or unsupported platforms.
- Prompt-injection risk from email, web pages, copied text, or untrusted attachments.
- Missing rollback, dry-run, or preview steps where those should exist.
- Claims that overstate privacy, safety, or reliability.

## Output format

- `Findings`: severity-ranked bullets with file references.
- `Open questions`: only if they block a recommendation.
- `Recommendation`: one line with `approve`, `approve with fixes`, or `do not install`.
- `First fixes`: the smallest changes that materially reduce risk.

## Defaults

- Be strict about public posting, messaging, payments, account changes, and secret handling.
- Prefer concrete failure modes over generic best-practice advice.
- If no material issues are found, say that explicitly and note any residual risk.
