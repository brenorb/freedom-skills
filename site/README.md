# The Freedom Ledger landing page

A dependency-free landing page for Freedom Skills, designed as the front page of an independent investigative weekly. The editorial system uses a cream, ink, and signal-red palette; local serif and monospace type; an asymmetric cover; and a filterable skills desk.

## Preview

From the repository root:

```sh
python3 -m http.server 8000 --directory site
```

Then open `http://localhost:8000`.

## Validate

The validator checks local asset references, in-page navigation targets, skill-source coverage, and basic accessibility landmarks. Node's syntax checker verifies both JavaScript files.

```sh
node site/validate.mjs
node --check site/script.js
node --check site/validate.mjs
git diff --check
```

The site uses no build step, package manager, runtime dependency, external font, cookie, or analytics script. External links lead only to the project's GitHub source and the Agent Skills standard.
