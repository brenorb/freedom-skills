---
name: add-freedom-skill
description: Use when adding, renaming or removing a skill in this repository's skills/ folder or a connector in connectors/, or changing how one appears on the website or in the README (category, tagline, example prompts, demo, caveats). Writes the skill's catalog card, regenerates the website data and README tables, and runs the link and skill checks.
---

# Add or change a Freedom Skill

The website, the README skill tables and the skill pages are generated from the cards in `site/catalog/`.
Never put a card or any other website file inside `skills/<slug>/`: `npx skills add` copies the
whole skill folder into the user's agent, so a skill folder holds only what the agent needs.
Never edit `site/content/skills.json`, `skill-details.json`, their `.js` twins, or the README
between `<!-- skills:start -->` and `<!-- skills:end -->` by hand.

## Add a skill

1. Write `skills/<slug>/SKILL.md` (frontmatter `name: <slug>` and a `description`; workflow
   action-first, as `AGENTS.md` asks).
2. Create its website card:
   ```bash
   uv run --with pyyaml python scripts/build_site_data.py --new <slug>
   ```
3. Fill in `site/catalog/skills/<slug>.yaml` from the SKILL.md and its references. Invent nothing:
   - `category`: one id from `site/catalog/categories.yaml` (add a category there only if none fits).
   - `order`: position inside the category; look at the neighbours' values.
   - `name`, `tagline` (≤ 90 characters, says what a person gets), `readme` (the README row).
   - `example_prompt` and 4–6 `prompts`: requests a person would really type.
   - `caveats`: the 2–4 most important warnings in SKILL.md. `needs`: prerequisites in one line.
   - `demo`: `prompt`, then `steps` with `kind` (`match`, `run`, `check`, `caveat`, `confirm`),
     `text`, and for `run` a real `cmd` from SKILL.md; the last step is `confirm` with an
     `action` verb (Send, Pay, Publish…). Then `result` in one line.
   - `music`: leave `null` until there is a track.
4. Regenerate everything:
   ```bash
   uv run --with pyyaml python scripts/build_site_data.py
   ```
5. Check:
   ```bash
   python3 scripts/check_site_links.py
   ./scripts/validate_skills_ref.sh skills/<slug>/SKILL.md
   ```
6. Commit the skill folder, its card and the regenerated files together.

## Add a connector

A connector is a prompt that links an agent runtime someone already runs to another service
(for example `connectors/whitenoise/`). It is not a skill and has no SKILL.md.

1. Write `connectors/<slug>/PROMPT.md`: a title, a line saying how to use it, then `---`, then the
   exact text a person pastes into their agent (the site's Copy prompt button copies only that part).
   Add a short `connectors/<slug>/README.md` for humans.
2. Optional card `site/catalog/connectors/<slug>.yaml`: `order`, `name`, `tagline`, `readme` (the README
   row), `works_with` (list of runtimes), `upstream`. Without it, the name comes from the README
   title and the tagline from its first sentence.
3. Run steps 4 and 5 of "Add a skill": the connector appears in the README connectors table and on live pages.

## Change or remove a skill

- Change wording on the site: edit `site/catalog/skills/<slug>.yaml`, then step 4.
- Remove a skill: delete `skills/<slug>/` and `site/catalog/skills/<slug>.yaml`, then step 4. Counts, numbering, category ranges and
  README rows update themselves.
- Rename: move the folder and rename its card in `site/catalog/skills/`, update `name:` in SKILL.md,
  then step 4 and step 5.

## How it stays in sync without you

- With `git config core.hooksPath .githooks`, every commit that touches `skills/` or `site/catalog/` regenerates and
  stages these files, and stops if a card is missing or a link is broken.
- In CI, pull requests fail when generated files are stale or a link points at nothing; pushes to
  `main` regenerate and commit anything that was missed.
- Every push to `main` publishes `site/` to https://freedomskills.dev (`.github/workflows/pages.yml`).
- The website is `site/`. Pages there with `<!--gen:… tpl=…-->` regions are regenerated; to change
  how the skill list looks, edit the `<template>` in that page, never the generated items.
