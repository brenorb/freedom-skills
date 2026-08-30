---
name: ai-request-coach
description: Use this skill when the user has a rough idea, messy draft, or high-stakes task and needs help turning it into a clear, safe request for an AI assistant. It is especially useful for non-technical users, activists, and guided workflows where privacy, scope control, and plain language matter.
---

# AI Request Coach

Turn vague or overloaded requests into a prompt the user can actually send.

## Default workflow

1. Start with the user's current wording. Do not lecture about prompting first.
2. Extract five things fast: goal, audience, source material, constraints, and desired output.
3. If a critical detail is missing, ask only the minimum follow-up questions needed to make the request usable. Keep it to three questions or fewer.
4. Rewrite the request in plain language. Prefer short sentences, explicit deliverables, and a clear success condition.
5. If the task is sensitive, add privacy-preserving limits such as:
   - remove names or identifiers
   - avoid uploading raw private documents when a summary will do
   - ask the model to say what it is unsure about
6. Return a ready-to-paste prompt first. After that, give a short note on what changed and any remaining risk.

## Prompt shape

Use this structure when rewriting:

```text
Goal: what needs to get done
Context: only the facts the model needs
Constraints: privacy, tone, time, format, red lines
Output: exact deliverable wanted
Checks: ask for uncertainty, assumptions, or missing info
```

## Defaults

- Prefer one strong prompt over a long prompt plus commentary.
- Prefer plain language over prompt jargon.
- Prefer guided outputs such as checklists, scripts, templates, and step-by-step plans.
- For non-technical users, name the tool or model only if it changes what they should do.

## Safety rules

- Do not help the user overshare sensitive personal, operational, legal, or security details.
- Do not fabricate confidence. If the task has real-world risk, require the model to surface assumptions and uncertainty.
- If the request could expose another person, reduce detail and suggest a safer framing.
- If the user wants persuasion, surveillance, or deception, refuse that part and offer a benign rewrite.
