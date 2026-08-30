---
name: secure-project-bootstrap
description: Use this skill when the user wants to start a new project with safer defaults from day one. It fits non-technical users, activists, and small teams who need a guided setup that reduces avoidable security and privacy mistakes without turning into enterprise process.
---

# Secure Project Bootstrap

Start the project with the smallest setup that can work safely.

## Default workflow

1. Begin with the project goal, who will use it, and what sensitive information it may touch.
2. Identify the minimum stack needed. Prefer simpler tools, fewer services, and fewer accounts.
3. Bootstrap only what is necessary to start:
   - local setup
   - secret handling
   - access boundaries
   - backup or recovery basics
   - a short operator checklist
4. Keep security controls concrete. Examples: `.env` for secrets, least-privilege accounts, private repos by default, encrypted storage when needed, and no unnecessary analytics.
5. Explain the first safe next step in plain language so the user can keep moving.

## Defaults

- Prefer local-first and open tools when they meet the need.
- Prefer private-by-default settings.
- Prefer checklists and starter docs over long theory.
- Prefer one maintainable path over multiple options unless tradeoffs are decisive.

## Minimum output

Return these sections when bootstrapping:

```text
What we are protecting
Recommended setup
Immediate risks to avoid
Step-by-step next actions
```

## Safety rules

- Do not publish, deploy, invite collaborators, or connect third-party services without explicit user confirmation.
- Do not put secrets, tokens, recovery codes, or personal data into the repo.
- Do not recommend complex hardening that the user is unlikely to maintain.
- If the project touches vulnerable people, location data, finances, or legal exposure, slow down and make the risk tradeoffs explicit.
