# Freedom Skills — Ember Relay

The project landing page tells one idea: hard-won operational knowledge should move freely while human authority stays put.

## Direction

**Ember Relay: A fire you can carry.** Cinder carries a live ember through five acts—from the gap between sovereign tools and ordinary use, through portable agent skills, to a public knowledge commons. The direction combines hand-built risograph-style SVG scenes with a restrained cinematic interface.

The page is intentionally dependency-free. Artwork, typography, canvas atmosphere, filters, and interactions all run from the files in this folder; there are no trackers, web fonts, remote scripts, or build step.

## Preview

From the repository root:

```sh
python3 -m http.server 8773
```

Then open `http://localhost:8773/site/`.

## Validate

```sh
node site/validate.mjs
```

The validator checks document landmarks, unique IDs, local links and artwork, skill count, required accessibility hooks, JavaScript syntax, and the absence of remote runtime dependencies.

## Accessibility and performance

- Semantic sections, a skip link, keyboard-operable tabs, visible focus states, and live filter results.
- Complete content without JavaScript; optional motion only enhances it.
- Reduced-motion behavior disables particle animation, transitions, magnetism, and staged reveals.
- Canvas rendering pauses off-screen, caps device pixel ratio, and uses bounded particle counts.
- SVG illustrations remain sharp at every viewport size and include reduced-motion fallbacks.

