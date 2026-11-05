# Freedom Festival landing page

A dependency-free landing page for Freedom Skills, designed as an optimistic night-market program for a global commons.

## Concept

Instead of presenting the repository as a conventional software catalog, the page invites visitors into a lantern-lit gathering. The five project categories become festival stages, and each of the 15 skills is an act on the program. Deep indigo supplies the night sky; hot coral, mint, and lantern yellow provide hand-painted wayfinding. The portable-skill explainer becomes a path through the grounds, and safety guidance becomes the shared etiquette of the commons.

The site uses only HTML, CSS, and a small progressive-enhancement script. There are no external fonts, assets, build tools, or runtime dependencies.

## Run locally

From the repository root:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000/site/`.

## Behavior and accessibility

- The stage selector filters the program and persists the selection in the `?stage=` URL parameter.
- Arrow keys, Home, and End move between selector buttons.
- Status changes are announced through an `aria-live` region.
- With JavaScript disabled, every skill remains visible and every link remains usable.
- Motion respects `prefers-reduced-motion`; the poster tilt is limited to fine pointers.
- The layout has dedicated mobile and print treatments, visible focus styles, semantic headings, and a skip link.

## Files

- `index.html` — semantic content and the full 15-skill program
- `styles.css` — visual system, layout, responsive states, and motion preferences
- `script.js` — optional category filtering, keyboard navigation, URL state, and poster interaction
