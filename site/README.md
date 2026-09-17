# Solar Commons landing page

This is a dependency-free concept site for Freedom Skills. Its visual direction is a **solarpunk civic conservatory**: trusted freedom-tech workflows are presented as living public infrastructure rather than specialist machinery.

The central interaction is the **capability canopy**. Visitors begin with a human outcome—communicating, protecting work, moving value, preserving evidence, or building—and see the relevant skills without needing to understand the underlying stack first. A selected path persists in the URL as `?path=protect`, so a filtered view can be shared.

## Preview

From the repository root:

```sh
python3 -m http.server 4173 --directory site
```

Then open `http://localhost:4173/`.

No build step, package install, remote font, framework, analytics script, or runtime dependency is required.

## Interaction and accessibility

- The path controls are native buttons with pressed state and a polite status update.
- Left/right arrow keys move between paths; Home and End jump to the first and last path.
- The selected outcome is restored from the `path` query parameter.
- With JavaScript unavailable, all 15 skills remain visible and the page explains that filtering is optional.
- Visible focus, skip navigation, semantic landmarks, descriptive labels, reduced-motion treatment, responsive layouts, and a print stylesheet are included.
- Content remains usable without backdrop-filter support or motion.

## Brand rationale

The page translates the canonical brand strategy directly:

- luminous green signals renewal, safety, and possibility;
- sunlight and sunset warmth signal earned optimism and relief;
- open sky, reflective glass, plant structure, and architectural scale create the living-infrastructure metaphor;
- audience language centers frontline advocates, exiled dissidents, enablement organizations, and sovereignty-minded users;
- copy leads with practical outcomes while AI remains a supporting layer;
- trust is expressed through curation, tests, visible safety assumptions, open-source inspection, and privacy-preserving measurement.

The design intentionally avoids cyberpunk terminals, bunker darkness, surveillance imagery, generic software dashboards, casino cues, and fear-driven language.

## Files

- `index.html` — complete content and semantic structure
- `styles.css` — visual system, responsive behavior, reduced-motion and print modes
- `script.js` — progressive path filtering, keyboard behavior, and URL persistence
