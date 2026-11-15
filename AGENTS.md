# Repo AGENTS Notes

## Skill authoring

- Default workflows in skills should be action-first.
- Start with the command that directly matches the user's goal.
- Only fall back to environment checks or onboarding if that action fails, or if the environment is genuinely uncertain.
- Do not make `command -v ...` or setup verification the mandatory first step when the tool is already known-good.

## Adding or changing a skill

- Follow `.claude/skills/add-freedom-skill/SKILL.md` for skills and for connectors (`connectors/<slug>/PROMPT.md`). Every skill has a website card in `catalog/skills/<slug>.yaml`; the website data, the README skill tables and the live site pages are generated from those cards by `scripts/build_site_data.py`.
- Never put website, README or catalog files inside `skills/<slug>/`. `npx skills add` copies the whole skill folder into the user's agent, so a skill folder holds only what the agent needs.
- Never hand-edit `site/content/skills.json`, `skill-details.json`, their `.js` twins, or the README between `<!-- skills:start -->`/`<!-- skills:end -->` and `<!-- connectors:start -->`/`<!-- connectors:end -->`.
- Before committing: `uv run --with pyyaml python scripts/build_site_data.py` and `python3 scripts/check_site_links.py`. Turn on the hooks once per clone with `git config core.hooksPath .githooks` to have this done on every commit.

## Language

- Write everything in English: skills, docs, code comments, commit messages, pull request and issue titles and bodies, and review comments.
- This applies even when the user writes to you in another language. Reply to them in their language if you like, but keep everything that lands in the repo or on GitHub in English.
- A squash merge takes its message from the commit messages, so write those in English too.
