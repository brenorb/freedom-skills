---
name: threat-model-lite
description: Use this skill when the user needs a fast, practical threat model in plain language instead of a formal security exercise. It fits activists, non-technical operators, and guided safety reviews where the goal is to spot the most likely harms and choose realistic mitigations.
---

# Threat Model Lite

Find the most likely ways a person, project, or device could get hurt, exposed, or disrupted, then cut risk with simple actions.

## Default workflow

1. Start with three questions:
   - What are you protecting?
   - Who are you worried about?
   - What happens if they succeed?
2. List the crown jewels first: people, accounts, devices, messages, files, money, reputation, and location.
3. Focus on likely threats, not every imaginable threat.
4. For each major risk, write:
   - asset
   - likely attacker or pressure source
   - common failure path
   - current protection
   - next best fix
5. Rank fixes by impact and effort. Prefer changes the user can actually do this week.
6. End with a short action plan, not a long report.

## Output shape

Use a compact table or bullet list with:

```text
Risk
Why it matters
What is already helping
Next step
Priority
```

## Defaults

- Prefer plain language over security jargon.
- Prefer operational habits and account hygiene before expensive tools.
- Prefer a small number of high-value fixes over exhaustive coverage.
- Name uncertainty when facts are missing.

## Safety rules

- Do not ask for unnecessary sensitive details.
- Do not give false confidence or claim a system is secure.
- If the scenario suggests imminent physical danger, stalking, targeted repression, or legal jeopardy, say so clearly and shift toward immediate harm reduction.
- Do not turn the exercise into attack instructions.
